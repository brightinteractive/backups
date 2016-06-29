#!/usr/bin/env python

from s3backups.metrics import Metrics

class AWSMetrics(Metrics):
    available_metrics = (
            'number_of_glacier_objects',
            'number_of_unrestored_objects',
            'restore_object_status_codes',
            'number_of_objects',
            'number_of_requests'
            )

    @classmethod
    def status_code(cls, metric):
        if metric not in cls.available():
            raise AttributeError('\'%s\' is not an available metric.'% metric)

        def wrapper(fn):
            def _status_code(*args, **kwargs):
                response = fn(*args, **kwargs)
                status_code = response['ResponseMetadata']['HTTPStatusCode']
                with cls._lock:
                    if cls.report[metric]:
                        if cls.report[metric].has_key(status_code):
                            cls.report[metric][status_code] += 1
                        else:
                            cls.report[metric][status_code] = 1
                    else:
                        cls.report[metric] = { status_code : 1 }
                return response
            return _status_code
        return wrapper


AWSMetrics.reset()
