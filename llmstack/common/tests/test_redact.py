import unittest

from llmstack.common.utils.redact import contains_secret, redact_secrets


class TestRedactSecrets(unittest.TestCase):
    def test_redacts_anthropic_key(self):
        # Arrange
        text = "Calling Claude with sk-ant-api03-AbCdEf123456_xyz in the header"
        # Act
        result = redact_secrets(text)
        # Assert
        self.assertNotIn("sk-ant-api03-AbCdEf123456_xyz", result)
        self.assertIn("[REDACTED]", result)

    def test_redacts_openai_key(self):
        # Arrange
        text = "key=sk-abcdefghijklmnopqrstuvwxyz0123456789"
        # Act
        result = redact_secrets(text)
        # Assert
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwxyz0123456789", result)
        self.assertIn("[REDACTED]", result)

    def test_redacts_github_token(self):
        # Arrange
        text = "git remote with ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
        # Act
        result = redact_secrets(text)
        # Assert
        self.assertNotIn("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", result)
        self.assertIn("[REDACTED]", result)

    def test_redacts_aws_access_key(self):
        # Arrange
        text = "aws id AKIAIOSFODNN7EXAMPLE here"
        # Act
        result = redact_secrets(text)
        # Assert
        self.assertNotIn("AKIAIOSFODNN7EXAMPLE", result)
        self.assertIn("[REDACTED]", result)

    def test_redacts_multiple_secrets_in_one_string(self):
        # Arrange
        text = "first sk-ant-api03-LongEnoughKey9 then AKIAIOSFODNN7EXAMPLE"
        # Act
        result = redact_secrets(text)
        # Assert
        self.assertEqual(result.count("[REDACTED]"), 2)

    def test_leaves_clean_text_unchanged(self):
        # Arrange
        text = "This is a perfectly ordinary log line with no secrets."
        # Act
        result = redact_secrets(text)
        # Assert
        self.assertEqual(result, text)

    def test_non_string_input_returned_unchanged(self):
        # Arrange
        payload = {"not": "a string"}
        # Act
        result = redact_secrets(payload)
        # Assert
        self.assertIs(result, payload)

    def test_contains_secret_detects_token(self):
        self.assertTrue(contains_secret("token ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"))

    def test_contains_secret_false_for_clean_text(self):
        self.assertFalse(contains_secret("nothing sensitive here"))


if __name__ == "__main__":
    unittest.main()
