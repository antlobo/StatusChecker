class AnyElementWithLocatorsVisible(object):
    def __init__(self, locators, multiple_elements: bool):
        self.locators = locators
        self.multiple_elements = multiple_elements

    def __call__(self, driver):
        for locator in self.locators:
            elements = driver.find_elements(locator.by, locator.value)

            for element in elements:
                if element.is_displayed():
                    if self.multiple_elements:
                        return elements
                    return element
        return False
