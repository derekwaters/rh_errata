import asyncio
import logging
import datetime
from typing import Any


BASE_URL = {
    "https://access.redhat.com/hydra/rest/securitydata"
}



async def main(queue: asyncio.Queue[Any], args: dict[str, Any]) -> None:
    """Poll the errata API and send events with new errata."""

    logger = logging.getLogger()
    logger.info("Processing errata queue")

    delay = int(args.get("interval", 1))

    common_get_args = {}
    if not verify_ssl:
        common_get_args["ssl"] = True

    poll_since = datetime.datetime.now()

    while True:
        endpoint_url = BASE_URL + "csaf.json&after=" + poll_since.isoformat()
        logger.info("Retrieving errata from " + endpoint_url)
        
        poll_since = datetime.datetime.now()

        async with aiohttp.ClientSession() as session:
            async with session.get(endpoint_url) as resp:
                for errata in resp:
                    await queue.put(
                        {
                            "errata_api": {
                                "data" : errata,
                            },
                        },
                    )

        await asyncio.sleep(delay)



async def main(queue: asyncio.Queue, args: Dict[str, Any]):
    logger = logging.getLogger()
    logger.info("Running Red Hat Errata API eda source")

    try:

        polling_interval = args.get("polling_interval", 60)
        # Filter by severity or type?





        for header, value in headers.items():
            _set_header(client, header, value)

        loop = asyncio.get_event_loop()

        while True:
            try:
                api = await loop.run_in_executor(
                    None,
                    functools.partial(
                        client.resources.get,
                        api_version=api_version,
                        kind=kind,
                    ),
                )

                result = await loop.run_in_executor(
                    None,
                    functools.partial(client.get, api, **options),
                )
                options["resource_version"] = int(
                    result["metadata"]["resourceVersion"]
                )

                watch_iter = await loop.run_in_executor(
                    None,
                    functools.partial(client.watch, api, **options),
                )

                while True:
                    try:
                        e = await loop.run_in_executor(
                            None, next, watch_iter
                        )
                    except StopIteration:
                        break
                    await queue.put(
                        dict(type=e["type"], resource=e["raw_object"])
                    )
            except Exception as e:
                logger.error("Exception caught: %s", e)
                await asyncio.sleep(1)
    finally:
        logger.info("Stopping k8s eda source")
        watcher.stop()


# Authentication functions from Kubernetes Core Module
# https://github.com/ansible-collections/kubernetes.core/blob/main/plugins/module_utils/k8s/client.py
def _create_auth_spec(args: Dict[str, Any]) -> Dict:
    auth: Dict = {}
    # If authorization variables aren't defined, look for them in environment variables
    for true_name, arg_name in AUTH_ARG_MAP.items():
        if arg_name in args and args.get(arg_name) is not None:
            auth[true_name] = args.get(arg_name)
        elif true_name in args and args.get(true_name) is not None:
            # Aliases in kwargs
            auth[true_name] = args.get(true_name)
        elif arg_name == "proxy_headers":
            # specific case for 'proxy_headers' which is a dictionary
            proxy_headers = {}
            for key in AUTH_PROXY_HEADERS_SPEC.keys():
                env_value = os.getenv(
                    "K8S_AUTH_PROXY_HEADERS_{0}".format(key.upper()), None
                )
                if env_value is not None:
                    if AUTH_PROXY_HEADERS_SPEC[key].get("type") == "bool":
                        env_value = env_value.lower() not in ["0", "false", "no"]
                    proxy_headers[key] = env_value
            if proxy_headers is not {}:
                auth[true_name] = proxy_headers
        else:
            env_value = os.getenv(
                "K8S_AUTH_{0}".format(arg_name.upper()), None
            ) or os.getenv("K8S_AUTH_{0}".format(true_name.upper()), None)
            if env_value is not None:
                if AUTH_ARG_SPEC[arg_name].get("type") == "bool":
                    env_value = env_value.lower() not in ["0", "false", "no"]
                auth[true_name] = env_value

    return auth


def _create_headers(args: Dict[str, Any]):
    header_map = {
        "impersonate_user": "Impersonate-User",
        "impersonate_groups": "Impersonate-Group",
    }

    headers = {}
    for arg_name, header_name in header_map.items():
        value = None
        if arg_name in args and args.get(arg_name) is not None:
            value = args.get(arg_name)
        else:
            value = os.getenv("K8S_AUTH_{0}".format(arg_name.upper()), None)
            if value is not None:
                if AUTH_ARG_SPEC[arg_name].get("type") == "list":
                    value = [x for x in value.split(",") if x != ""]
        if value:
            headers[header_name] = value
    return headers


def _set_header(client, header, value):
    if isinstance(value, list):
        for v in value:
            client.set_default_header(
                header_name=unique_string(header), header_value=v
            )
    else:
        client.set_default_header(header_name=header, header_value=value)


class unique_string(str):
    _low = None

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        return self is other

    def lower(self):
        if self._low is None:
            lower = str.lower(self)
            if str.__eq__(lower, self):
                self._low = self
            else:
                self._low = unique_string(lower)
        return self._low


def _create_configuration(auth: Dict):
    def auth_set(*names: list) -> bool:
        return all(auth.get(name) for name in names)

    if auth_set("host"):
        # Removing trailing slashes if any from hostname
        auth["host"] = auth.get("host").rstrip("/")

    if (
        auth_set("username", "password", "host")
        or auth_set("api_key", "host")
        or auth_set("cert_file", "key_file", "host")
    ):
        # We have enough in the parameters to authenticate, no need to load incluster or kubeconfig
        pass
    elif auth_set("kubeconfig") or auth_set("context"):
        try:
            _load_config(auth)
        except Exception as err:
            raise err

    else:
        # First try to do incluster config, then kubeconfig
        try:
            config.load_incluster_config()
        except config.ConfigException:
            try:
                _load_config(auth)
            except Exception as err:
                raise err

    # Override any values in the default configuration with Ansible parameters
    # As of kubernetes-client v12.0.0, get_default_copy() is required here
    try:
        configuration = client.Configuration().get_default_copy()
    except AttributeError:
        configuration = client.Configuration()

    for key, value in auth.items():
        if key in AUTH_ARG_MAP.keys() and value is not None:
            if key == "api_key":
                setattr(
                    configuration,
                    key,
                    {"authorization": "Bearer {0}".format(value)},
                )
            elif key == "proxy_headers":
                headers = urllib3.util.make_headers(**value)
                setattr(configuration, key, headers)
            else:
                setattr(configuration, key, value)

    return configuration


def _load_config(auth: Dict) -> None:
    kubeconfig = auth.get("kubeconfig")
    optional_arg = {
        "context": auth.get("context"),
        "persist_config": auth.get("persist_config"),
    }
    if kubeconfig:
        if isinstance(kubeconfig, str):
            config.load_kube_config(config_file=kubeconfig, **optional_arg)
        elif isinstance(kubeconfig, dict):
            config.load_kube_config_from_dict(
                config_dict=kubeconfig, **optional_arg
            )
    else:
        config.load_kube_config(config_file=None, **optional_arg)


if __name__ == "__main__":

    class MockQueue:
        async def put(self, event):
            print(event)

    asyncio.run(main(MockQueue(), {}))