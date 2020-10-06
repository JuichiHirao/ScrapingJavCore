import yaml
import slack
from slack import errors

class SlackApi:

    def __init__(self):
        with open('credentials.yml') as file:
            obj = yaml.load(file, Loader=yaml.FullLoader)
            self.token = obj['slack_token']

        self.slack_client = slack.WebClient(token=self.token)

    def post(self, str_list, channel):

        response = 'no response'
        if type(str_list) is list:
            for str in str_list:
                response = self.__post__(str, channel)
        else:
            response = self.__post__(str_list, channel)

        return response

    def __post__(self, str_data, channel):

        try:
            response = self.slack_client.chat_postMessage(
                channel=channel,
                text=str_data)
        except errors.SlackApiError as e:
            response = e.response

        return response
