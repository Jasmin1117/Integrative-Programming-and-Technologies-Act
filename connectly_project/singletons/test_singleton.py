from singletons.config_manager import ConfigManager

# Create two instances
config1 = ConfigManager()
config2 = ConfigManager()

# Verify Singleton Behavior (both instances should be the same)
assert config1 is config2, "Singleton failed! config1 and config2 should be the same instance."

# Modify a setting in one instance
config1.set_setting("DEFAULT_PAGE_SIZE", 50)

# Check if the change is reflected in the other instance
assert config2.get_setting("DEFAULT_PAGE_SIZE") == 50, "Singleton failed! Changes are not shared."

print("Singleton test passed! ConfigManager is working as expected.")
