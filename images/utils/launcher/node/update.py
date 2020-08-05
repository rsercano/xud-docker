from typing import Dict
import logging

from .image import ImageManager


class ImageUpdate:
    pass


class ContainerUpdate:
    missing: bool
    image: str
    environment: str
    ports: str
    volumes: str
    command: str


class ServiceUpdate:
    container: ContainerUpdate


class UpdateDetails:
    services: Dict[str, ServiceUpdate]

    def __str__(self):
        print("- Service")


class UpdateManager:
    def __init__(self, image_manager: ImageManager, node_manager):
        self.image_manager = image_manager
        self.node_manager = node_manager
        self.logger = logging.getLogger("launcher.node.UpdateManager")

    def _get_image_updates(self):
        # Step 1. check all images
        print("🌍 Checking for updates...")

        images = self.image_manager.check_for_updates()

        for image in images:
            status = image.status
            if status in ["LOCAL_MISSING", "LOCAL_OUTDATED"]:
                print("- Image %s: %s" % (image.name, image.status_message))
                outdated = True
                image_outdated = True
            elif status == "UNAVAILABLE":
                all_unavailable_images = [x for x in images if x.status == "UNAVAILABLE"]
                raise FatalError("Image(s) not available: %r" % all_unavailable_images)

    def _get_container_updates(self):
        # Step 2. check all containers
        containers = self.nodes.values()
        container_check_result = {c: None for c in containers}

        def print_failed(failed):
            print("Failed to check for container updates.")
            for container, error in failed:
                print("- {}: {}".format(container.name, get_useful_error_message(error)))

        def try_again():
            answer = self.shell.yes_or_no("Try again?")
            return answer == "yes"

        def handle_result(container, result):
            container_check_result[container] = result

        parallel_execute(containers, lambda c: c.check_for_updates(), 60, print_failed, try_again, handle_result)

        self.logger.debug("[Update] Container checking result: %r", container_check_result)

        for container, result in container_check_result.items():
            status, details = result
            # when mode internal -> external or others, status will be "external_with_container"
            # when mode external or others -> internal, status will be "missing" because we deleted the container before
            # when disabled False -> True, status will be "disabled_with_container"
            # when disabled True -> False, status will be "missing" because we deleted the container before
            if status in ["missing", "outdated", "external_with_container", "disabled_with_container"]:
                readable_details = self._readable_details(details)
                if readable_details:
                    print("- Container %s: %s (%s)" % (container.container_name, self._display_container_status_text(status), readable_details))
                else:
                    print("- Container %s: %s" % (container.container_name, self._display_container_status_text(status)))
                outdated = True

    def _get_network_updates(self):
        pass

    def check_for_updates(self) -> UpdateDetails:
        image_updates = self._get_image_updates()




        # outdated = False
        # image_outdated = False
        #
        #
        #
        #
        #
        # if not outdated:
        #     print("All up-to-date.")
        #     return True
        #
        # all_containers_missing = functools.reduce(lambda a, b: a and b[0] in ["missing", "external", "disabled"], container_check_result.values(), True)
        #
        # if all_containers_missing:
        #     if self.newly_installed:
        #         answer = "yes"
        #     else:
        #         if image_outdated:
        #             answer = "yes"
        #         else:
        #             return  # FIXME unintended containers (configuration) update
        # else:
        #     answer = self.shell.yes_or_no(UPDATE_PROMPT)



    def apply(self, updates):
        # Step 1. update images
        self.image_manager.update_images()

        # Step 2. update containers
        # 2.1) stop all running containers
        for container in containers:
            container.stop()
        # 2.2) recreate outdated containers
        for container, result in container_check_result.items():
            container.update(result)