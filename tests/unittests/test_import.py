import unittest


class HIVTestImports(unittest.TestCase):
    def setUp(self) -> None:
        self.expected_items = None
        self.found_items = None
        pass

    def verify_expected_items_present(self, namespace):
        self.found_items = dir(namespace)
        for item in self.expected_items:
            self.assertIn(
                item,
                self.found_items
            )

    def tearDown(self) -> None:
        pass

    def test_requirements(self):
        import emod_api
        import emodpy_hiv
        import emodpy
        # Testing that we can import all requirements
        checks = [dir(package) for package in [emod_api, emodpy_hiv, emodpy]]
        for package in checks:
            self.assertIn('__package__', package)
        return

    # region interventions
    def test_intervention_outbreak(self):
        from emodpy_hiv.interventions import outbreak

        self.expected_items = [
            "new_intervention", "ob"
        ]
        self.verify_expected_items_present(namespace=outbreak)
        return
    # endregion

    # region demographics
    def test_demographics_imports(self):
        import emodpy_hiv.demographics.HIVDemographics as Demographics

        self.expected_items = [
            "HIVDemographics", "from_template_node", "from_pop_csv", "from_params"
        ]
        self.verify_expected_items_present(namespace=Demographics)

    def test_demographics_template_imports(self):
        import emodpy_hiv.demographics.DemographicsTemplates as DemographicsTemplates

        self.expected_items = [
            "add_society_from_template", "add_default_society"
        ]
        self.verify_expected_items_present(namespace=DemographicsTemplates)

    # endregion


if __name__ == '__main__':
    unittest.main()
