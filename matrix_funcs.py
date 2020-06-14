import matrix as _matrix
import matrix_config as _matrix_config


def send (message):
    m_matrix = _matrix.Matrix(_matrix_config.base_url,_matrix_config.user_name,_matrix_config.password)
    if m_matrix.login():
        m_matrix.room_id = _matrix_config.room_id
        m_matrix.send_message(message)