import logging
import os
import re
import subprocess
import time

from src.models.application import Application
from src.models.configuration.configurations_object import ConfigurationsObject


class Intellij(Application):
    """
    Class for managing IntelliJ application
    """

    def __init__(self):
        super().__init__()
        self.config_run_region = self.two_coordinate_locator(
            locator_type="point",
            x_coordinate=110,
            y_coordinate=470,
        )
        self.configurations = []

    def get_ide_version(self, ide_directory):
        pattern = re.compile(r"\d{3}\.\d{4}\.\d{2}")
        return [name for name in os.listdir(ide_directory) if pattern.search(name) is not None][0]

    def close_ide(self):
        """
        Closes the IDE
        """
        self.click(self.config_run_region)
        self.press_keys("alt", "f")
        self.press_keys("x")
        self.press_keys("enter")
        time.sleep(1)
        self.press_keys("enter")

    def delete_all_configurations(self):
        self.click(self.config_run_region)
        self.press_keys("ctrl", "a")
        self.click(action="right_click")
        self.press_keys("up")
        self.press_keys("enter")
        time.sleep(1)
        self.configurations = []

    def create_configuration_in_ui(self):
        self.click(self.config_run_region)
        self.click(action="right_click")
        self.press_keys("down")
        self.press_keys("enter")
        time.sleep(1)

    def create_configuration_in_file(
        self,
        analysis_data,
        app_name,
        application_config,
        config,
        uuid,
    ):
        configurations_object = ConfigurationsObject()
        configuration = configurations_object.create(
            analysis_data,
            app_name,
            application_config,
            config,
            uuid,
        )
        self.configurations.append(configuration)
        self.refresh_configuration()

    def image_locator(self, locator):
        return f"image:{self.IMG_DIR}/intellij/{locator}"

    def is_open_mta_perspective(self):
        """
        Checks if MTA perspective is already opened in IntelliJ

        Returns:
            (bool): True or False
        """
        try:
            self.wait_find_element(locator_type="image", locator="mta_perspective_active.png")
            return True
        except Exception as exc:
            try:
                self.wait_find_element(
                    locator_type="image",
                    locator="mta_perspective_active_alt.png",
                )
                return True
            except Exception:
                logging.debug(
                    "An error occured while finding \
                    MTA perspective tab ! {}".format(
                        str(exc),
                    ),
                )
            if "No matches found" in str(exc):
                return False
            else:
                raise Exception(exc)

    def open_mta_perspective(self):
        """
        Opens MTA perspective in IntelliJ
        """
        if self.is_open_mta_perspective():
            logging.info("MTA perspective is already opened !")
        else:
            # Click on the MTA tab in left sidebar
            self.click_element(locator_type="image", locator="mta_tab.png")

        self.click(self.config_run_region)

    def run_simple_analysis(self, app_name, wait_for_analysis_finish=False):

        self.refresh_configuration()

        # Search for configuration name that has to be run
        self.type_text(app_name)
        self.press_keys("enter")
        # Find config name highlighted and select correct config if multiple matches are found
        self.click(action="right_click")
        self.press_keys("up")
        self.press_keys("up")
        self.press_keys("enter")
        # Wait for analysis to be completed in IDE terminal
        if wait_for_analysis_finish:
            time.sleep(2)
            self.wait_find_element(
                locator_type="image",
                locator="analysis_complete_terminal.png",
                timeout=120.0,
            )

    def open_report_page(self, app_name):

        self.click(self.config_run_region)
        self.type_text(app_name)
        self.press_keys("enter")
        self.press_keys("enter")
        self.click_element(locator_type="image", locator="report_selector.png")
        # Verify the report page is opened
        self.wait_find_element(locator_type="image", locator="report_page_header.png")

    def refresh_configuration(self):
        """
        re-read the configuration from the json file
        """
        self.click(self.config_run_region)
        self.click(action="right_click")
        self.press_keys("up")
        self.press_keys("enter")

    def set_focus(self):
        # instead of blindly clicking on alt+tab, this brings the intellij into focus
        subprocess.run(
            "wmctrl -R $(wmctrl -lx | grep  jetbrains-idea | cut -d' ' -f7)",
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def cancel_analysis(self):
        """
        Cancels an in-progress analysis
        """
        time.sleep(3)
        self.click_element(locator_type="image", locator="cancel_analysis.png")
        self.click()

    def open_plugin_info(self, plugin):
        self.press_keys("ctrl", "alt", "s")
        self.press_keys("ctrl", "f")
        self.type_text("plugins")
        self.press_keys("enter")
        self.type_text(f"Migration Toolkit for {plugin}")
        self.press_keys("enter")
