import functools
import logging
import sys
import time


default_logging_wrapper_config = {
    'enter': 'Entering %s',
    'leave': 'Leaving %s',
    'error': '%s'
}

def logging_wrapper(logging_conf={}, fail_exit=False, exitcode=0):
    def logging_decorator(func):
        conf = logging_conf.get(func.__name__) or default_logging_wrapper_config
        @functools.wraps(func) # invoke func.__name__ out of this decorator
                               # returns real func-name instead of 'logging_call'
        def logging_call(*args, **kwargs):
            try:
                args_repr = [repr(a) for a in args]
                kwargs_repr = ["%s=%s" % (k, repr(v)) for k, v in kwargs.items()]
                arguments = ", ".join(args_repr + kwargs_repr)
                logging.info(conf['enter'], func.__name__)
                logging.debug('Calling %s(%s)', func.__name__, arguments)
                value = func(*args, **kwargs)
            except Exception as e:
                logging.exception(conf['error'], e)
                if fail_exit:
                    sys.exit(exitcode)
            else:
                logging.debug('%s returned value: %s', func.__name__, repr(value))
                logging.info(conf['leave'], func.__name__)
                return value
        return logging_call
    return logging_decorator


def time_this(func):
    @functools.wraps(func)
    def timer(*args, **kwargs):
        before = time.perf_counter() 
        result = func(*args, **kwargs)
        after = time.perf_counter()
        run_time = after - before
        logging.info("Finished %s in %.4f secs", func.__name__, run_time)
        return result
    return timer


if __name__ == '__main__':
    @logging_wrapper()
    @time_this
    def test_func(a, b=8):
        logging.info('Inside function %s', __name__)
        return (a, b)

    log_format = '%(asctime)-15s %(levelname)s\t%(funcName)s:%(lineno)d\t%(message)s'
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    test_func(1, b=7)
