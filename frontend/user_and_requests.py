import requests


class User:
    """
    A class to manage user data and API interactions.

    This class provides methods to interact with the user API endpoints,
    including managing user interests, dislikes, and allergies.

    Parameters
    ----------
    email : str
        The user's email address.
    user_id : int, optional
        The user's unique identifier. If not provided, it will be
        fetched from the API using the email address.

    Attributes
    ----------
    user_id : int
        The user's unique identifier.
    email : str
        The user's email address.
    base_url : str
        The base URL for API requests (default: "http://localhost:8000").
    """

    def __init__(
        self,
        email: str,
        user_id: int | None = None,
    ):
        self.user_id = user_id
        self.email = email
        self.base_url = "http://localhost:8000"

        if self.email and not self.user_id:
            self._fetch_user_id()

    def _fetch_user_id(self):
        """
        Fetch user_id from email if not already set.

        This private method makes an API call to retrieve the user's ID
        based on their email address. The user_id is then stored in the
        instance attribute.

        Notes
        -----
        This method is called automatically during initialization if
        user_id is not provided but email is available.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        if self.email:
            response = requests.get(f"{self.base_url}/user/{self.email}")
            if response.status_code == 200:
                user_data = response.json()
                self.user_id = user_data.get("id")

    def get_interests(self) -> list:
        """
        Get user interests from the API.

        Retrieves all interests associated with the user from the API
        and stores them in the instance's interests attribute.

        Returns
        -------
        list
            A list of dictionaries containing interest information.
            Each dictionary contains at least 'id' and 'interest_name' keys.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """

        response = requests.get(f"{self.base_url}/interest/{self.user_id}")
        response.raise_for_status()
        self.interests = response.json()
        return response.json()

    def add_interests(self, interest: str) -> dict:
        """
        Add a new interest for the user.

        Creates a new interest entry for the user via API call and
        refreshes the local interests list.

        Parameters
        ----------
        interest : str
            The name of the interest to add.

        Returns
        -------
        dict
            The response from the API containing the created interest data.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.post(
            f"{self.base_url}/interest/",
            json={"user_id": self.user_id, "interest_name": interest},
        )
        response.raise_for_status()
        self.interests = self.get_interests()
        return response.json()

    def delete_interests(self, interest_id: int) -> dict:
        """
        Delete a user interest by its ID.

        Removes an interest from the user's profile via API call and
        refreshes the local interests list.

        Parameters
        ----------
        interest_id : int
            The unique identifier of the interest to delete.

        Returns
        -------
        dict
            The response from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.delete(
            f"{self.base_url}/interest/{interest_id}",
        )
        response.raise_for_status()
        self.interests = self.get_interests()

    def get_dislikes(self) -> list:
        """
        Get user dislikes from the API.

        Retrieves all dislikes associated with the user from the API
        and stores them in the instance's dislikes attribute.

        Returns
        -------
        list
            A list of dictionaries containing dislike information.
            Each dictionary contains at least 'id' and 'dislike_name' keys.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.get(f"{self.base_url}/dislike/{self.user_id}")
        response.raise_for_status()
        self.dislikes = response.json()
        return response.json()

    def add_dislikes(self, dislike: str) -> dict:
        """
        Add a new dislike for the user.

        Creates a new dislike entry for the user via API call and
        refreshes the local dislikes list.

        Parameters
        ----------
        dislike : str
            The name of the dislike to add.

        Returns
        -------
        dict
            The response from the API containing the created dislike data.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.post(
            f"{self.base_url}/dislike/",
            json={"user_id": self.user_id, "dislike_name": dislike},
        )
        response.raise_for_status()
        self.dislikes = self.get_dislikes()
        return response.json()

    def delete_dislikes(self, dislike_id: int) -> dict:
        """
        Delete a user dislike by its ID.

        Removes a dislike from the user's profile via API call and
        refreshes the local dislikes list.

        Parameters
        ----------
        dislike_id : int
            The unique identifier of the dislike to delete.

        Returns
        -------
        dict
            The response from the API.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.delete(
            f"{self.base_url}/dislike/{dislike_id}",
        )
        response.raise_for_status()
        self.dislikes = self.get_dislikes()
        return response.json()

    def get_allergies(self) -> list:
        """
        Get user allergies from the API.

        Retrieves all allergies associated with the user from the API
        and stores them in the instance's allergies attribute.

        Returns
        -------
        list
            A list of dictionaries containing allergy information.
            Each dictionary contains at least 'name' key.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """

        response = requests.get(f"{self.base_url}/user/{self.user_id}/allergies")
        response.raise_for_status()
        self.allergies = response.json()
        return response.json()

    def add_allergies(self, allergy: str) -> dict:
        """
        Add a new allergy for the user.

        Creates a new allergy entry for the user via API call and
        refreshes the local allergies list.

        Parameters
        ----------
        allergy : str
            The name of the allergy to add.

        Returns
        -------
        dict
            The response from the API containing the updated allergies list.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.post(
            f"{self.base_url}/user/{self.user_id}/allergies?allergy_name={allergy}"
        )
        response.raise_for_status()
        self.allergies = response.json()
        return response.json()

    def delete_allergies(self, allergy_name: str) -> dict:
        """
        Delete a user allergy by its name.

        Removes an allergy from the user's profile via API call and
        refreshes the local allergies list.

        Parameters
        ----------
        allergy_name : str
            The name of the allergy to delete.

        Returns
        -------
        dict
            The response from the API containing the updated allergies list.

        Raises
        ------
        requests.RequestException
            If the API request fails.
        """
        response = requests.delete(
            f"{self.base_url}/user/{self.user_id}/allergies?allergy_name={allergy_name}"
        )
        response.raise_for_status()
        self.allergies = response.json()
        return response.json()
