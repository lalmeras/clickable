# -*- coding: utf-8 -*-

"""Tests for `clickable.click` package."""


import os
import sys
import unittest
import unittest.mock

import pytest

import clickable.click


class TestClickableClick:
    """Tests for `clickable.click` package."""

    def test_clickable_debug(self):
        """Test environment variable lookup to boolean. true/yes/1
        (case insensitive) maps to 1, else False."""
        for k, v in [("true", True), ("True", True), ("1", True),
          ("YES", True), ("Yes", True), ("yes", True),
          ("false", False), ("0", False), ("no", False)]:
            with unittest.mock.patch.dict(os.environ, {"CLICKABLE_DEBUG": k}):
                assert clickable.click._clickable_debug() == v, \
                    "Unexpected result for value {}".format(v)

    def test_callable_name_clickable_mapping(self):
        """Test priority rule for mapping lookup."""
        class Module:
            CLICKABLE_MAPPING = "callable_mapping"
            CLICK_MAPPING = "ignored"
        o = Module()
        assert clickable.click._find_callable_mapping(o) == "callable_mapping"

    def test_callable_name_click_mapping(self):
        """Test fallback rule for mapping lookup."""
        class Module:
            CLICK_MAPPING = "callable_mapping"
        o = Module()
        assert clickable.click._find_callable_mapping(o) == "callable_mapping"

    def test_callable_name_no_mapping(self):
        """Test None result if no mapping found."""
        class Module:
            pass
        o = Module()
        assert clickable.click._find_callable_mapping(o) is None

    def test_find_callable_name_no_mapping(self):
        """Test fallback."""
        assert clickable.click._find_callable_name(None, "whatever") == "whatever"

    def test_find_callable_name_mapping_not_found(self):
        """Test mapping present, but no entry for key."""
        assert clickable.click._find_callable_name({}, "whatever") is None

    def test_find_callable_name_mapping_static(self):
        """Test static mapping (constant string)."""
        assert clickable.click._find_callable_name("method", "whatever") == "method"

    def test_find_callable_name_mapping_found(self):
        """Test static mapping (constant string)."""
        assert clickable.click._find_callable_name({"whatever": "works"}, "whatever") == "works"

    def test_get_callable_key(self):
        """Test name transformation."""
        with unittest.mock.patch.object(sys, "argv", ["simplename"]):
            assert clickable.click._get_callable_key() == "simplename"
        with unittest.mock.patch.object(sys, "argv", ["simple-name"]):
            assert clickable.click._get_callable_key() == "simple_name"
        with unittest.mock.patch.object(sys, "argv", ["simple0name"]):
            assert clickable.click._get_callable_key() == "simple0name"
        with unittest.mock.patch.object(sys, "argv", ["0simplename"]):
            assert clickable.click._get_callable_key() == "_0simplename"

    @unittest.mock.patch("sys.stderr")
    @unittest.mock.patch("clickable.click._find_callable_name")
    @unittest.mock.patch("clickable.click._find_callable_mapping")
    @unittest.mock.patch("clickable.click._get_callable_key")
    def test_find_callable(self, c_key, c_mapping, c_name, stderr):
        """Key and mapping lookup success. Callable is found and returned.
        Check messages."""
        c_name.return_value = "callable_name"
        c_key.return_value = "callable_key"
        module = unittest.mock.MagicMock()
        module.callable_name = unittest.mock.MagicMock()
        func = clickable.click._find_callable(module)

        stderr.write.is_not_called()
        assert func == module.callable_name

    @unittest.mock.patch("sys.stderr")
    @unittest.mock.patch("clickable.click._find_callable_name")
    @unittest.mock.patch("clickable.click._find_callable_mapping")
    @unittest.mock.patch("clickable.click._get_callable_key")
    def test_find_callable_fallback(self, c_key, c_mapping, c_name, stderr):
        """If no mapping and `callable_key` not found, fallback to `main`."""
        c_key.return_value = "callable_key"
        c_mapping.return_value = None
        c_name.return_value = "callable_key"
        module = unittest.mock.MagicMock()
        # callable_key not a callable
        module.callable_key = None
        # main fallback
        module.main = unittest.mock.MagicMock()
        func = clickable.click._find_callable(module)

        stderr.write.is_not_called()
        assert func == module.main

    @unittest.mock.patch("sys.stderr")
    @unittest.mock.patch("clickable.click._find_callable_name")
    @unittest.mock.patch("clickable.click._find_callable_mapping")
    @unittest.mock.patch("clickable.click._get_callable_key")
    def test_find_callable_name_not_found(self, c_key, c_mapping, c_name, stderr):
        """Callable name not found. Check messages."""
        mapping = unittest.mock.MagicMock()
        c_mapping.return_value = mapping
        c_name.return_value = None
        c_key.return_value = "callable_key"
        module = unittest.mock.MagicMock()
        func = clickable.click._find_callable(module)

        stderr.write.is_called()
        messages = _write_messages(sys.stderr)
        assert "callable_key" in messages
        assert str(c_name.return_value) in messages
        assert "invalid" in messages
        assert func == False

    @unittest.mock.patch("sys.stderr")
    @unittest.mock.patch("clickable.click._find_callable_name")
    @unittest.mock.patch("clickable.click._find_callable_mapping")
    @unittest.mock.patch("clickable.click._get_callable_key")
    def test_find_callable_not_callable(self, c_key, c_mapping, c_name, stderr):
        """Key and mapping lookup success but callable not found. Check messages."""
        mapping = unittest.mock.MagicMock()
        c_mapping.return_value = mapping
        c_name.return_value = "callable_name"
        c_key.return_value = "callable_key"
        module = unittest.mock.MagicMock()
        module.callable_name = "__not callable__"
        func = clickable.click._find_callable(module)

        stderr.write.is_called()
        messages = _write_messages(sys.stderr)
        assert "is not a callable" in messages
        assert "__not callable__" in messages
        assert func == False

    def test_main(self, capsys):
        with unittest.mock.patch.object(sys, "argv", []):
            with pytest.raises(SystemExit) as e:
                clickable.click.main()
            assert e.value.code == 2
            captured = capsys.readouterr()
            assert "clickables.py" in captured.err


def _write_messages(stream):
    # concat written messages from a stream mock
    return " ".join([_call_args_args(m)[0] for m in stream.write.call_args_list])


def _call_args_args(call_args):
    # args only exist from py38;
    # use tuple lookup: positional args in first tuple
    return call_args[0]
