import streamlit as st

SUGGESTED_INTERESTS = [
    "Piña coladas",
    "Gettin' caught in the rain",
    "Having half a brain",
    "Making love at midnight in the dunes of the cape",
    "Acme Sand-Away",
    "Champagne",
    "A bar called O'Malley's",
    "Escaping",
]
SUGGESTED_DISLIKES = [
    "My lady (We've been together too long)",
    "A worn out recording of a favorite song",
    "Yoga",
    "Health food",
    "Red tape",
]
SUGGESTED_ALLERGIES = [
    "Milk",
    "Eggs",
    "Shellfish",
    "Gluten",
    "Peanuts",
    "Soybeans",
    "Sesame",
    "Tree Nuts",
    "Nightshade",
]


def user_preferences_initial_load():
    """
    Initialize user preferences data if not already loaded.

    This function checks if the user's interests, dislikes, and allergies
    are already loaded in the session state. If not, it fetches them from
    the API and stores them in the user object.

    Notes
    -----
    This function modifies st.session_state.user by adding interests,
    dislikes, and allergies attributes if they don't exist.
    """
    if not hasattr(st.session_state.user, "interests"):
        st.session_state.user.get_interests()
    if not hasattr(st.session_state.user, "dislikes"):
        st.session_state.user.get_dislikes()
    if not hasattr(st.session_state.user, "allergies"):
        st.session_state.user.get_allergies()


def preference_form(preference_name: str, list_of_choices: list[str]):
    """
    Create a preference form for any preference type.

    This function creates a Streamlit form that allows users to manage their
    preferences (interests, dislikes, or allergies). It displays checkboxes
    for suggested choices and a text input for custom choices.

    Parameters
    ----------
    preference_name : str
        The name of the preference category (e.g., "interests", "dislikes",
        "allergies"). Must be one of: "interests", "dislikes", "allergies".
    list_of_choices : list[str]
        List of suggested choices for the preference category.
        These will be displayed as checkboxes in the form.

    Notes
    -----
    The function automatically handles:
    - Loading existing user preferences
    - Displaying checkboxes for suggested choices
    - Allowing custom input via text field
    - Adding new preferences via API calls
    - Removing deselected preferences via API calls

    The form expects the user object to have methods like:
    - get_interests(), add_interests(), delete_interests()
    - get_dislikes(), add_dislikes(), delete_dislikes()
    - get_allergies(), add_allergies(), delete_allergies()
    """
    user = st.session_state.user  # convenience variable
    with st.form(f"{preference_name}_form"):
        preference_json = getattr(user, preference_name)
        if preference_name == "interests":
            preference_list = [item["interest_name"] for item in preference_json]
        elif preference_name == "dislikes":
            preference_list = [item["dislike_name"] for item in preference_json]
        elif preference_name == "allergies":
            preference_list = [item["name"] for item in preference_json]
        custom_choices = []
        checkbox_states = {choice: False for choice in list_of_choices}
        for choice in preference_list:
            if choice not in list_of_choices:
                custom_choices.append(choice)
            else:
                checkbox_states[choice] = True
        for suggested, is_checked in checkbox_states.items():
            checkbox_states[suggested] = st.checkbox(
                suggested,
                value=is_checked,
            )

        other_choices = st.text_input(
            f"List any other {preference_name.lower()} divided by semi-colons",
            value="; ".join(custom_choices),
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            currently_selected = set()

            for choice, is_checked in checkbox_states.items():
                if is_checked:
                    currently_selected.add(choice)

            if other_choices:
                for choice in other_choices.split(";"):
                    choice = choice.strip()
                    if choice:
                        currently_selected.add(choice)

            if preference_name == "interests":
                name_field = "interest_name"
            elif preference_name == "dislikes":
                name_field = "dislike_name"
            elif preference_name == "allergies":
                name_field = "name"

            to_delete = set(preference_list) - currently_selected
            for pref_name in to_delete:
                if preference_name == "interests" or preference_name == "dislikes":
                    for pref in preference_json:
                        if pref[name_field] == pref_name:
                            getattr(user, "delete_" + preference_name)(pref["id"])
                            break
                elif preference_name == "allergies":
                    getattr(user, "delete_" + preference_name)(pref_name)

            for choice in currently_selected:
                if choice not in preference_list:
                    getattr(user, "add_" + preference_name)(choice)


def main():
    """
    Main function to display the user preferences interface.

    This function sets up the complete user preferences page, including
    the page header and forms for managing interests, dislikes, and allergies.

    Notes
    -----
    The function uses the global constants SUGGESTED_INTERESTS,
    SUGGESTED_DISLIKES, and SUGGESTED_ALLERGIES to populate the
    preference forms with default options.
    """
    st.header("My Preferences")
    user_preferences_initial_load()
    preference_form("interests", SUGGESTED_INTERESTS)
    preference_form("dislikes", SUGGESTED_DISLIKES)
    preference_form("allergies", SUGGESTED_ALLERGIES)


if __name__ == "__main__":
    main()
