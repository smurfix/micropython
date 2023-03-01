# Adapted with permission from the EdgeDB project.
# MIT license; Copyright (c) 2023 Matthias Urlichs
import sys
def pr(*x):
    print(*x,file=sys.stderr)

from . import core
from . import Event

_DEBUG = const(False)
_s_new = const(0)
_s_entered = const(1)
_s_exiting = const(2)
_s_aborting = const(3)


class TaskGroup:
    def __init__(self):
        self._state = _s_new
        self._loop = None
        self._parent_task = None
        self._parent_cancel_requested = False
        self._tasks = set()
        self._pending = set()
        self._errors = []
        self._base_error = None
        self._on_completed = None

    def __repr__(self):
        if _DEBUG:
            info = [""]
            if self._tasks:
                info.append("tasks=" + str(len(self._tasks)))
            if self._errors:
                info.append("errors={}" + str(len(self._errors)))
            if self._state == _s_aborting:
                info.append("cancelling")
            elif self._state > _s_new:
                info.append("entered")
            return "<TaskGroup{}>".format(" ".join(info))
        else:
            return "<TaskGroup>"

    async def __aenter__(self):
        if self._state != _s_new:
            raise RuntimeError("TaskGroup has been already entered")
        self._state = _s_entered

        if self._loop is None:
            self._loop = core.get_event_loop()

        self._parent_task = core.current_task()
        if self._parent_task is None:
            raise RuntimeError("TaskGroup cannot determine the parent task")

        return self

    async def __aexit__(self, et, exc, tb):
        if self._state == _s_entered:
            self._state = _s_exiting
        propagate_cancellation_error = None

        pr(1,exc)
        if exc is not None and self._is_base_error(exc) and self._base_error is None:
            self._base_error = exc

        if et is not None:
            pr(314)
            if self._state < _s_aborting:
                if et is core.CancelledError:
                    # Handle "external" cancellation.
                    propagate_cancellation_error = exc

                # Otherwise the main task raised an error.
                self._abort()

            # Tasks that didn't yet enter our _run_task wrapper
            # get cancelled off immediately
            pr(310)
            for task in self._pending:
                pr(311,task.name)
                task.cancel()
                self._tasks.discard(task)
        else:
            pr(313)
            for task in self._pending:
                pr(312,task.name)
        # We use while-loop here because "self._on_completed"
        # can be cancelled multiple times if our parent task
        # is being cancelled repeatedly (or even once, when
        # our own cancellation is already in progress)
        while self._tasks:
            pr(2,self._tasks,self._pending)
            for t in self._tasks:
                pr(34,t.done(),t.name)
            if self._on_completed is None:
                pr(21)
                self._on_completed = Event()
                pr(22)

            try:
                pr(23)
                await self._on_completed.wait()
                pr(24)
            except core.CancelledError as ex:
                pr(25,self._state)
                if self._state < _s_aborting:
                    # Our parent task is being cancelled.
                    propagate_cancellation_error = ex
                    pr(30)
                    self._abort()
                pr(26)
            except BaseException as ex:
                pr(28,ex)
                raise
            else:
                pr(27)

            pr(29)
            self._on_completed = None

        pr(31)
        assert not self._tasks

        if self._base_error is not None:
            # SystemExit and Keyboardinterrupt get propagated as they are
            pr(6)
            raise self._base_error

        if et is not None and et is not core.CancelledError:
            pr(7,exc)
            self._errors.append(exc)

        if self._errors:
            pr(97,self._errors)
            # Exceptions are heavy objects that can have object
            # cycles (bad for GC); let's not keep a reference to
            # a bunch of them.
            errors = self._errors
            self._errors = None

            if len(errors) == 1:
                me = errors[0]
            else:
                if _DEBUG:
                    import sys

                    for err in errors:
                        sys.print_exception(err)
                EGroup = core.ExceptionGroup
                for err in errors:
                    if not isinstance(err, Exception):
                        EGroup = core.baseExceptionGroup
                        break
                me = EGroup("unhandled errors in a TaskGroup", errors)
            raise me

        elif propagate_cancellation_error is not None:
            # The wrapping task was cancelled; since we're done with
            # closing all child tasks, just propagate the cancellation
            # request now.
            pr(98)
            raise propagate_cancellation_error
        pr(99)

    def create_task(self, coro, name="-"):
        if self._state == _s_new:
            raise RuntimeError("TaskGroup has not been entered")
        if self._state == _s_aborting and not self._tasks:
            raise RuntimeError("TaskGroup is finished")

        k = [None]
        t = self._loop.create_task(self._run_task(k, coro))
        t.name=name
        k[0] = t  # sigh
        self._tasks.add(t)
        self._pending.add(t)
        return t

    def cancel(self):
        # Extension (not in CPython): kill off a whole taskgroup
        # TODO this waits for the parent to die before killing the child
        # tasks. Shouldn't that be the other way round?
        try:
            self._parent_task.cancel()
        except RuntimeError:
            raise core.CancelledError()

    def _is_base_error(self, exc: BaseException) -> bool:
        # KeyboardInterrupt and SystemExit are "special": they should
        # never be wrapped with a [Base]ExceptionGroup.
        assert isinstance(exc, BaseException)
        return isinstance(exc, (SystemExit, KeyboardInterrupt))

    def _abort(self):
        self._state = _s_aborting

        pr(397)
        for t in self._pending:
            t.cancel()
            self._tasks.discard(t)
        for t in self._tasks:
            if t is not core.cur_task and not t.done():
                pr(399,t.name)
                t.cancel()
            else:
                pr(398,t.name)

    async def _run_task(self, k, coro):
        task = k[0]
        pr(301,task.name)
        assert task is not None
        self._pending.remove(task)

        try:
            await coro
            pr(302,task.name)
        except core.CancelledError as e:
            pr(100,e)
            exc = e
        except BaseException as e:
            pr(101,e)
            if _DEBUG:
                import sys

                sys.print_exception(e)

            exc = e
        else:
            pr(102,e)
            exc = None
        finally:
            pr(121,self._on_completed,self._tasks)
            for t in self._tasks:
                pr(123,t.name,t.done(),t.coro)
            self._tasks.discard(task)
            if self._on_completed is not None:
                pr(122)
                self._on_completed.set()

        if type(exc) is core.CancelledError:
            pr(103)
            return

        if exc is None:
            pr(104)
            return

        pr(105,exc)
        self._errors.append(exc)
        if self._is_base_error(exc) and self._base_error is None:
            pr(106)
            self._base_error = exc

        if self._parent_task.done():
            pr(107)
            # Not sure if this case is possible, but we want to handle
            # it anyways.
            self._loop.call_exception_handler(
                {
                    "message": "Task has errored out but its parent is already completed",
                    "exception": exc,
                    "task": task,
                }
            )
            pr(108)
            return

        pr(109,self._state,self._parent_cancel_requested)
        if self._state < _s_aborting and not self._parent_cancel_requested:
            pr(111)
            # If parent task *is not* being cancelled, it means that we want
            # to manually cancel it to abort whatever is being run right now
            # in the TaskGroup.  But we want to mark parent task as
            # "not cancelled" later in __aexit__.  Example situation that
            # we need to handle:
            #
            #    async def foo():
            #        try:
            #            async with TaskGroup() as g:
            #                g.create_task(crash_soon())
            #                await something  # <- this needs to be canceled
            #                                 #    by the TaskGroup, e.g.
            #                                 #    foo() needs to be cancelled
            #        except Exception:
            #            # Ignore any exceptions raised in the TaskGroup
            #            pass
            #        await something_else     # this line has to be called
            #                                 # after TaskGroup is finished.
            self._abort()
            self._parent_cancel_requested = True
            self._parent_task.cancel()
        pr(110)
