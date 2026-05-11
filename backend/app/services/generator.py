import time
import uuid

from app.services.nlp import NLPModule
from app.services.ami_builder import AMIBuilder
from app.schemas.ami import AMIGraph


def generate_interface(text: str) -> dict[str, object]:
    start = time.perf_counter()

    time.sleep(0.03)  # Имитация работы

    # NLP модуль для распознавания сущностей
    nlp = NLPModule()
    entities = nlp.predict(text)
    
    # Построение AMI-графа
    ami_builder = AMIBuilder()
    ami_graph = ami_builder.build(entities)

    # Заглушка HTML/CSS (пока не подключаем Jinja2)
    html = '''<form class="login-form" aria-labelledby="login-title" role="form">
  <h2 id="login-title" class="login-form__title">Login</h2>
  <div class="login-form__field">
    <label class="login-form__label" for="email">Email</label>
    <input type="email" id="email" placeholder="Enter your email" class="login-form__input" aria-describedby="email-help" aria-required="true" />
    <div id="email-help" class="sr-only">Enter a valid email address</div>
  </div>
  <div class="login-form__field">
    <label class="login-form__label" for="password">Password</label>
    <input type="password" id="password" placeholder="Enter your password" class="login-form__input" aria-describedby="password-help" aria-required="true" />
    <div id="password-help" class="sr-only">Enter your password</div>
  </div>
  <button type="submit" class="login-form__button" aria-label="Sign in to your account">Sign In</button>
</form>'''

    css = '''body {
  margin: 0;
  padding: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
}

.login-form {
  max-width: 400px;
  margin: 0 auto;
  padding: 2rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.login-form__title {
  font-size: 1.5rem;
  font-weight: bold;
  margin-bottom: 1.5rem;
  color: #333;
}

.login-form__field {
  margin-bottom: 1rem;
}

.login-form__label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.login-form__input {
  width: 100%;
  padding: 0.5rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
  transition: border-color 0.15s ease-in-out, box-shadow 0.15s ease-in-out;
}

.login-form__input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.login-form__button {
  width: 100%;
  background: #3b82f6;
  color: white;
  font-weight: bold;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.15s ease-in-out;
}

.login-form__button:hover {
  background: #2563eb;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}'''

    generation_time_ms = (time.perf_counter() - start) * 1000

    return {
        'request_id': str(uuid.uuid4()),
        'html': html,
        'css': css,
        'generation_time_ms': round(generation_time_ms, 2),
        'ami': ami_graph,
    }
