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


def user_preferences_initial_load(preference_name: str, list_of_choices: list[str]):
    if "user_preferences" not in st.session_state:
        st.session_state.user_preferences = {
            "Allergies": {},
            "Dislikes": {},
            "Interests": {},
        }
    for choice in list_of_choices:
        if choice not in st.session_state.user_preferences[preference_name]:
            st.session_state.user_preferences[preference_name][choice] = False


def preference_form(preference_name: str, list_of_choices: list[str]):
    """
    Vectorized function to create a preference form for any preference type.

    Args:
        preference_name: The name of the preference category
        (e.g., "Interests", "Dislikes", "Allergies")
        list_of_choices: List of suggested choices for the preference
    """
    user_preferences_initial_load(preference_name, list_of_choices)
    st.subheader(preference_name)
    with st.form(f"{preference_name.lower()}_form"):
        custom_choices = []
        checkbox_states = {}
        for choice in st.session_state.user_preferences[preference_name]:
            if choice not in list_of_choices:
                custom_choices.append(choice)
            else:
                checkbox_states[choice] = st.checkbox(
                    choice,
                    value=st.session_state.user_preferences[preference_name][choice],
                )

        other_choices = st.text_input(
            f"List any other {preference_name.lower()} divided by semi-colons",
            value=";".join(custom_choices),
        )
        submitted = st.form_submit_button("Submit")
        if submitted:
            if other_choices:
                for choice in other_choices.split(";"):
                    choice = choice.strip()
                    if choice:
                        st.session_state.user_preferences[preference_name][
                            choice
                        ] = True
            for choice, is_checked in checkbox_states.items():
                st.session_state.user_preferences[preference_name][choice] = is_checked


def main():
    st.header("My Preferences")
    preference_form("Interests", SUGGESTED_INTERESTS)
    preference_form("Dislikes", SUGGESTED_DISLIKES)
    preference_form("Allergies", SUGGESTED_ALLERGIES)


if __name__ == "__main__":
    main()
