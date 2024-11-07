user_states = {}
user_data = {}

def get_user_state(user_id):
    return user_states.get(user_id)

def set_user_state(user_id, state):
    user_states[user_id] = state

def get_user_data(user_id):
    return user_data.get(user_id, {})

def set_user_data(user_id, key, value):
    if user_id not in user_data:
        user_data[user_id] = {}
    user_data[user_id][key] = value

def clear_user_data(user_id):
    if user_id in user_data:
        del user_data[user_id]

