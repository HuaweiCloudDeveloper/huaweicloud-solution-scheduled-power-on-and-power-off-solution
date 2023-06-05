# coding: utf-8

from huaweicloudsdkcore.auth.credentials import BasicCredentials
from huaweicloudsdkecs.v2.region.ecs_region import EcsRegion
from huaweicloudsdkcore.exceptions import exceptions
from huaweicloudsdkecs.v2 import *

import traceback


def handler(event, context):
    log = context.getLogger()
    result = check_configuration(context)
    if result is not None:
        return result

    processor = Processor(context)

    try:
        response = processor.stop_servers()
        return f"'{response}'"
    except:
        log.error("failed to process, "
                  f"exception：{traceback.format_exc()}")


def check_configuration(context):
    ak = context.getSecurityAccessKey()
    sk = context.getSecuritySecretKey()
    if not ak or not sk:
        ak = context.getUserData('ak', '').strip()
        sk = context.getUserData('sk', '').strip()
        if not ak or not sk:
            return 'ak or sk is empty'


class Processor:
    def __init__(self, context=None):
        self.log = context.getLogger()
        self.os_client = os_client(context)
        self.region = context.getUserData('region').strip()
        self.ids = context.getUserData('ids').strip().split()

    def build_servers_options(self):
        listServersOsstart = []

        for os_id in self.ids:
            listServersOsstart.append(
                ServerId(
                    id=os_id
                )
            )

        return listServersOsstart

    def stop_servers(self):
        try:
            request = BatchStopServersRequest()

            osstopbody = BatchStopServersOption(
                servers=self.build_servers_options()
            )
            request.body = BatchStopServersRequestBody(
                os_stop=osstopbody
            )

            return self.os_client.batch_stop_servers(request)
        except exceptions.ClientRequestException as e:
            print(e.status_code)
            print(e.request_id)
            print(e.error_code)
            print(e.error_msg)
            self.log.error(f"failed to request batch stop servers"
                           f"status_code：{e.status_code}, "
                           f"request_id:{e.request_id}, "
                           f"error_code:{e.error_code}. "
                           f"error_msg:{e.error_msg}")


def os_client(context):
    ak = context.getSecurityAccessKey()
    sk = context.getSecuritySecretKey()
    st = context.getSecurityToken()
    project_id = context.getProjectID()
    credentials = BasicCredentials(ak, sk, project_id).with_security_token(st)
    return EcsClient.new_builder() \
        .with_credentials(credentials) \
        .with_region(EcsRegion.value_of(context.getUserData('region'))) \
        .build()
