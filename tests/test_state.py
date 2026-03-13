"""Tests for the StateManager module."""

import json
from unittest.mock import patch
from pathlib import Path
from nexus.state import StateManager

def test_state_manager_init_and_load_success(tmp_path: Path) -> None:
    test_state_file = tmp_path / "state.json"
    
    # Pre-populate state file
    with open(test_state_file, "w") as f:
        json.dump({"recents": ["/path/a", "/path/b"]}, f)
        
    with patch("nexus.state.STATE_FILE", test_state_file):
        manager = StateManager()
        assert manager.get_recents() == ["/path/a", "/path/b"]


def test_state_manager_init_no_file(tmp_path: Path) -> None:
    test_state_file = tmp_path / "does_not_exist.json"
        
    with patch("nexus.state.STATE_FILE", test_state_file):
        manager = StateManager()
        assert manager.get_recents() == []


def test_state_manager_add_recent(tmp_path: Path) -> None:
    test_state_file = tmp_path / "state.json"
    
    with patch("nexus.state.STATE_FILE", test_state_file):
        manager = StateManager()
        
        manager.add_recent("/path/1")
        assert manager.get_recents() == ["/path/1"]
        
        manager.add_recent("/path/2")
        assert manager.get_recents() == ["/path/2", "/path/1"]
        
        # Test moving to front
        manager.add_recent("/path/1")
        assert manager.get_recents() == ["/path/1", "/path/2"]
        
        # Test limit
        for i in range(15):
            manager.add_recent(f"/path/x/{i}")
            
        assert len(manager.get_recents()) == 10
        assert manager.get_recents()[0] == "/path/x/14"


def test_state_manager_save_failure(tmp_path: Path) -> None:
    test_state_file = tmp_path / "state.json"
    
    with patch("nexus.state.STATE_FILE", test_state_file):
        manager = StateManager()
        
        with patch("pathlib.Path.mkdir", side_effect=PermissionError("denied")):
            with patch("nexus.state.log.error") as mock_log_error:
                manager.add_recent("/path/test")
                
                # The state will be updated in memory
                assert manager.get_recents() == ["/path/test"]
                
                # But we should see a log error
                mock_log_error.assert_called_once()
                assert mock_log_error.call_args[0][0] == "save_state_failed"


def test_state_manager_load_failure(tmp_path: Path) -> None:
    test_state_file = tmp_path / "state.json"
    
    # Create invalid JSON
    with open(test_state_file, "w") as f:
        f.write("{invalid: json}")
        
    with patch("nexus.state.STATE_FILE", test_state_file):
        with patch("nexus.state.log.error") as mock_log_error:
            manager = StateManager()
            assert manager.get_recents() == []
            mock_log_error.assert_called_once()
            assert mock_log_error.call_args[0][0] == "load_state_failed"
