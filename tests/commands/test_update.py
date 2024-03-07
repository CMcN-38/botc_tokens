"""Tests for the update command."""
# Standard Library
from contextlib import contextmanager
import json
from pathlib import Path
from unittest import mock

# Third Party
from testhelpers import check_output_folder

# Application Specific
from botc_tokens.commands import update


expected_json = {
    "First.json": {
        'ability': 'First ability description',
        'affects_setup': False,
        'first_night': True,
        'home_script': '54 - Unreal Experimental',
        'icon': 'First.png',
        'name': 'First',
        'other_nights': True,
        'reminders': [],
        'type': 'townsfolk'
    },
    "Second.json": {
        'ability': 'Second ability description [Affects Setup]',
        'affects_setup': True,
        'first_night': False,
        'home_script': '54 - Unreal Experimental',
        'icon': 'Second.png',
        'name': 'Second',
        'other_nights': True,
        'reminders': ["SECOND REMINDER"],
        'type': 'demon'
    }
}


@contextmanager
def web_mock():
    """Mock out actual web access."""
    # First create the return data we would expect from the web, in the order we expect it.
    urlopen_read_mock = mock.MagicMock()
    urlopen_read_mock.read.side_effect = [
        # The first call is for the role data
        b"""[
             {
                "id": "First",
                "name": "First",
                "roleType": "townsfolk",
                "print": "unused",
                "icon": "unused",
                "version": "54 - Unreal Experimental",
                "isDisabled": false
              },
              {
                "id": "Second",
                "name": "Second",
                "roleType": "demon",
                "print": "unused",
                "icon": "unused",
                "version": "54 - Unreal Experimental",
                "isDisabled": false
              },
              {
                "id": "Third",
                "name": "Third",
                "roleType": "outsider",
                "print": "unused",
                "icon": "unused",
                "version": "99 - Ignored",
                "isDisabled": false
              }
            ]""",
        # The second call is for the night data
        b"""{
              "firstNight": [
                "DUSK",
                "First"
              ],
              "otherNight": [
                "DUSK",
                "First",
                "Second"
              ]
            }""",
        # The third call is for the first role's wiki page
        b"""<html>
              <body>
                <div><h2 id="Summary">First ability</h2></div>
                <p>First ability description</p>
                <div><h2 id="How_to_Run">How To Run</h2></div>
                <div id="character-details"><img src="First.png" /></div>
              </body>
            </html>""",
        # The fourth call is for the second role's wiki page
        b"""<html>
              <body>
                <div><h2 id="Summary">Second ability</h2></div>
                <p>Second ability description [Affects Setup]</p>
                <div><h2 id="How_to_Run">How To Run</h2></div>
                <p><b>SECOND REMINDER</b></p>
                <div id="character-details"><img src="Second.png" /></div>
              </body>
            </html>""",
        # The fifth call is for the third role's wiki page, which we will show as blank
        b"""<html>
              <body>
              </body>
            </html>""",
    ]

    # Now mock out all the web calls to instead return the data we created
    with mock.patch("botc_tokens.helpers.wiki_soup.urlopen") as urlopen_mock:
        urlopen_mock.return_value.__enter__.return_value.read = urlopen_read_mock
        urlopen_mock.return_value = urlopen_read_mock
        # Make sure to patch out urlretrieve, as we don't want to actually download the images
        with mock.patch("botc_tokens.commands.update.urlretrieve"):
            yield


def check_expected_json(input_file_path):
    """Ensure each file exists and, if it is a json file, matches what we expect."""
    assert input_file_path.is_file()
    if input_file_path.suffix == ".json":
        assert input_file_path.name in expected_json
        with open(input_file_path, "r") as f:
            j = json.load(f)
        assert j == expected_json.get(input_file_path.name)


def test_update_command(tmp_path):
    """Test the update command in its normal configuration."""
    output_path = tmp_path / "roles"
    with mock.patch("sys.argv", ["botc_tokens", "update", "--output", str(output_path)]):
        with web_mock():
            update.run()

    # Verify that it worked
    expected_files = [
        str(Path("54 - Unreal Experimental") / "townsfolk" / "First.json"),
        str(Path("54 - Unreal Experimental") / "demon" / "Second.json"),
    ]
    check_output_folder(output_path, expected_files=expected_files, check_func=check_expected_json)


def test_update_existing_folder(tmp_path):
    """Test when a file in the output folder already exists."""
    output_path = tmp_path / "roles"
    output_path.mkdir()
    first_file = output_path / "54 - Unreal Experimental" / "townsfolk" / "First.json"
    first_file.parent.mkdir(parents=True, exist_ok=True)
    with open(first_file, "w") as f:
        json.dump(expected_json.get("First.json"), f)
    with mock.patch("sys.argv", ["botc_tokens", "update", "--output", str(output_path)]):
        with web_mock():
            update.run()

    # Verify that it worked
    expected_files = [
        str(Path("54 - Unreal Experimental") / "townsfolk" / "First.json"),
        str(Path("54 - Unreal Experimental") / "demon" / "Second.json"),
    ]
    check_output_folder(output_path, expected_files=expected_files, check_func=check_expected_json)


def test_update_bad_json(tmp_path, capsys):
    """Test when a file in the output folder exists, but isn't in the format we expect."""
    output_path = tmp_path / "roles"
    output_path.mkdir()
    first_file = output_path / "54 - Unreal Experimental" / "townsfolk" / "First.json"
    first_file.parent.mkdir(parents=True, exist_ok=True)
    with open(first_file, "w") as f:
        f.write("This is not json")
    with mock.patch("sys.argv", ["botc_tokens", "update", "--output", str(output_path)]):
        with web_mock():
            update.run()

    # Verify that we got the files we expected
    expected_files = [
        str(Path("54 - Unreal Experimental") / "townsfolk" / "First.json"),
        str(Path("54 - Unreal Experimental") / "demon" / "Second.json"),
    ]
    check_output_folder(output_path, expected_files=expected_files)

    # Make sure the file we wrote is still there, unmodified
    with open(first_file, "r") as f:
        assert f.read() == "This is not json"

    # Make sure we notified the user that the file was bad
    output = capsys.readouterr()
    assert "Could not read" in output.out


def test_update_script_filter(tmp_path):
    """Test the script filter option."""
    output_path = tmp_path / "roles"
    with mock.patch("sys.argv", ["botc_tokens", "update", "--output", str(output_path), "--script-filter", "99 - Ignored"]):
        with web_mock():
            update.run()

    # Verify that it worked
    expected_files = [
        str(Path("99 - Ignored") / "outsider" / "Third.json"),
    ]
    check_output_folder(output_path, expected_files=expected_files)


def test_update_missing(tmp_path, capsys):
    """Test when the wiki doesn't return the expected data."""
    output_path = tmp_path / "roles"
    with mock.patch("sys.argv", ["botc_tokens", "update", "--output", str(output_path), "--script-filter", ""]):
        with web_mock():
            update.run()

    # Check if we alerted to user to not being able to find the role info
    output = capsys.readouterr()
    assert "No ability found" in output.out
    assert "No icon found" in output.out
    assert "No reminder info found" in output.out


