# Copyright 2017 theloop Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import functools
import inspect

from transitions import Machine

import loopchain.utils as util


class ExceptionNullStatesInMachine(Exception):
    pass


class ExceptionNullInitState(Exception):
    pass


class StateMachine(object):
    def __init__(self, arg):
        self.arg = arg
        util.logger.spam(f"arg is {self.arg}")

    def __call__(self, cls):
        class Wrapped(cls):
            attributes = self.arg

            def __init__(self, *cls_args):
                if not hasattr(cls, 'states') or not cls.states:
                    raise ExceptionNullStatesInMachine

                if not hasattr(cls, 'state') or not cls.state:
                    raise ExceptionNullInitState

                util.logger.spam(f"Wrapped __init__ called")
                util.logger.spam(f"cls_args is {cls_args}")
                # self.name = "superman"

                cls.machine = Machine(model=self, states=cls.states, initial=cls.state,
                                      ignore_invalid_triggers=True)

                cls.__init__(cls, *cls_args)

        return Wrapped


def transition(func=None):
    # if func is None:
    #     return functools.partial(transition)

    @functools.wraps(func)
    def _wrapper(*args, **kwargs):
        bound_arguments = inspect.signature(func).bind(*args, **kwargs)
        bound_arguments.apply_defaults()
        arguments = dict(bound_arguments.arguments)
        util.logger.spam(f"_wrapper func({func}) bound_arguments({arguments})")

        trigger_name = func.__name__
        arguments['self'].machine.add_transition(trigger=trigger_name,
                                                 source=arguments['source'],
                                                 dest=arguments['dest'],
                                                 before=arguments.get('before'),
                                                 after=arguments.get('after'),
                                                 conditions=arguments.get('conditions'))

        trigger = getattr(arguments['self'], trigger_name)
        util.logger.spam(f"_wrapper func.__name__({func.__name__})")
        trigger()
        # func(*args, **kwargs)

    return _wrapper
