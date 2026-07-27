from app.core.expansions import expand_roles, expand_levels


def test_devops_expansion():
    result = expand_roles("devops")
    assert "DevOps" in result
    assert "Site Reliability Engineer" in result


def test_backend_expansion():
    result = expand_roles("backend")
    assert "Backend Developer" in result


def test_junior_expansion():
    result = expand_levels("júnior")
    assert "Junior" in result
    assert "Entry Level" in result


def test_estagio_expansion():
    result = expand_levels("estágio")
    assert "Intern" in result
    assert "Internship" in result


def test_unknown_role_returns_original():
    result = expand_roles("custom role xyz")
    assert result == ["custom role xyz"]


def test_unknown_level_returns_original():
    result = expand_levels("especialista")
    assert result == ["especialista"]
