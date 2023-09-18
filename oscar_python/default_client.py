import abc
import oscar_python._utils as utils

_RUN_PATH = "/run"
_POST = "post"


class DefaultClient(metaclass=abc.ABCMeta):

    _AUTH_TYPE = ''

    """ Run a synchronous execution. 
    If an output is provided the result is decoded onto the file.
    In both cases the function returns the HTTP response."""
    def run_service(self, name, **kwargs):
        if "input" in kwargs.keys() and kwargs["input"]:
            exec_input = kwargs["input"]
            if "token" in kwargs.keys() and kwargs["token"]:
                token = kwargs["token"]
            else: token = self._get_token(name)
            
            if type(exec_input) is dict:
                send_data = exec_input
            else: send_data = utils.encode_input(exec_input)

            if "timeout" in kwargs.keys() and kwargs["timeout"]:
                response = utils.make_request(self, _RUN_PATH+"/"+name, _POST, data=send_data, token=token, timeout=kwargs["timeout"])
            else:
                response = utils.make_request(self, _RUN_PATH+"/"+name, _POST, data=send_data, token=token)
            
            if "output" in kwargs.keys() and kwargs["output"]:
                utils.decode_output(response.text, kwargs["output"])
            return response
        
        return utils.make_request(self, _RUN_PATH+"/"+name, _POST, token=token)