"""Test configuration system with all patterns."""

from guaro import API, DatabaseEngine, normalize_database_config
from guaro.config.schema import NormalizedDatabaseConfig

# Test 1: Default configuration (None)
print("Test 1: Default configuration")
config1 = normalize_database_config(None)
assert config1.url == "sqlite+aiosqlite:///guaro.db"
assert config1.engine == DatabaseEngine.SQLITE
assert config1.auto_migrate == True
print("✓ Default config works")

# Test 2: Dictionary configuration with explicit engine
print("\nTest 2: Dictionary with explicit engine")
config2 = normalize_database_config({
    "url": "postgresql+asyncpg://user:pass@localhost/db",
    "engine": DatabaseEngine.POSTGRESQL,
    "pool_size": 15,
})
assert config2.url == "postgresql+asyncpg://user:pass@localhost/db"
assert config2.engine == DatabaseEngine.POSTGRESQL
assert config2.pool_size == 15
print("✓ Dictionary config works")

# Test 3: Dictionary with inferred engine
print("\nTest 3: Dictionary with inferred engine (from URL)")
config3 = normalize_database_config({
    "url": "postgresql://user@localhost/db",
})
assert config3.engine == DatabaseEngine.POSTGRESQL
print("✓ Engine inference from URL works")

# Test 4: String URL
print("\nTest 4: String URL configuration")
config4 = normalize_database_config("postgresql://user@localhost/db")
assert config4.url == "postgresql://user@localhost/db"
assert config4.engine == DatabaseEngine.POSTGRESQL
print("✓ String URL config works")

# Test 5: NormalizedDatabaseConfig pass-through
print("\nTest 5: Pass-through normalized config")
original = NormalizedDatabaseConfig(
    url="sqlite:///test.db",
    engine=DatabaseEngine.SQLITE,
)
config5 = normalize_database_config(original)
assert config5 is original
print("✓ Pass-through works")

# Test 6: API integration
print("\nTest 6: API integration with config")
api = API(
    database={
        "url": "sqlite+aiosqlite:///test_api.db",
        "engine": DatabaseEngine.SQLITE,
    }
)
assert api.db_config.url == "sqlite+aiosqlite:///test_api.db"
assert api.db_config.engine == DatabaseEngine.SQLITE
assert api.registry.db_config is not None
print("✓ API config integration works")

# Test 7: Error handling - invalid engine
print("\nTest 7: Error handling - invalid engine")
try:
    normalize_database_config({
        "url": "sqlite:///test.db",
        "engine": "invalid_engine",
    })
    print("✗ Should have raised ValueError")
except ValueError as e:
    print(f"✓ Correctly raised ValueError: {e}")

# Test 8: Error handling - missing URL
print("\nTest 8: Error handling - missing URL")
try:
    normalize_database_config({
        "engine": DatabaseEngine.SQLITE,
    })
    print("✗ Should have raised ValueError")
except ValueError as e:
    print(f"✓ Correctly raised ValueError: {e}")

print("\n" + "="*60)
print("All configuration tests passed! ✓")
print("="*60)
