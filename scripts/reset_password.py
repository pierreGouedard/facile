# Global import
import sys

# Local import
from facileapp.models import Users

if __name__ == "__main__":
    assert len(sys.argv[1:]) == 2, 'pass 2 argument, space are not allowed'

    # Get username
    username = sys.argv[1]
    password = sys.argv[2]

    # Get user
    user = Users.from_username(username)

    # Change passward
    user.password = password

    # Update database
    user.update_user()
