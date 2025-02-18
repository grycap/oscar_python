import abc
import oscar_python._utils as utils

_RUN_PATH = "/run"
_JOB_PATH = "/job"
_POST = "post"


class DefaultClient(metaclass=abc.ABCMeta):

    _AUTH_TYPE = ''

    """ Run an execution.
    If async is set to True the execution is run asynchronously.
    If an output is provided the result is decoded onto the file.
    In both cases the function returns the HTTP response."""
    def run_service(self, name, **kwargs):
        if kwargs.get("token"):
            token = kwargs["token"]
        else:
            token = self._get_token(name)

        send_data = None
        if kwargs.get("input"):
            send_data = kwargs["input"]
            if not isinstance(send_data, dict):
                send_data = utils.encode_input(send_data)

        path = _RUN_PATH + "/"+name
        if kwargs.get("async_call"):
            path = _JOB_PATH + "/" + name

        response = utils.make_request(self, path, _POST, data=send_data,
                                      token=token, timeout=kwargs.get("timeout"))

        if kwargs.get("output"):
            utils.decode_output(response.text, kwargs["output"])

        return response
