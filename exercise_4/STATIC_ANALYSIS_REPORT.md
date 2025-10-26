=== PYLINT (backend) ===
************* Module app
backend/app.py:1:0: F0002: backend/app.py: Fatal error while checking 'backend/app.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in '/Users/jianlin/Library/Caches/pylint/pylint-crash-2025-09-10-15-58-01.txt'. (astroid-error)
************* Module ._app
backend/._app.py:1:0: E0001: Parsing failed: 'invalid or missing encoding declaration for '/Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/._app.py'' (syntax-error)
************* Module agents.._stock_agent
backend/agents/._stock_agent.py:1:0: E0001: Parsing failed: 'invalid or missing encoding declaration for '/Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/agents/._stock_agent.py'' (syntax-error)
************* Module agents.stock_agent
backend/agents/stock_agent.py:1:0: F0002: backend/agents/stock_agent.py: Fatal error while checking 'backend/agents/stock_agent.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in '/Users/jianlin/Library/Caches/pylint/pylint-crash-2025-09-10-15-58-01.txt'. (astroid-error)

=== PYLINT (frontend_py) ===
************* Module ._app
frontend_py/._app.py:1:0: E0001: Parsing failed: 'invalid or missing encoding declaration for '/Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/frontend_py/._app.py'' (syntax-error)
************* Module app
frontend_py/app.py:1:0: F0002: frontend_py/app.py: Fatal error while checking 'frontend_py/app.py'. Please open an issue in our bug tracker so we address this. There is a pre-filled template that you can use in '/Users/jianlin/Library/Caches/pylint/pylint-crash-2025-09-10-15-58-01.txt'. (astroid-error)

=== PYRIGHT (backend) ===
/Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/agents/stock_agent.py
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/agents/stock_agent.py:3:8 - warning: Import "requests" could not be resolved from source (reportMissingModuleSource)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/agents/stock_agent.py:38:16 - error: Import "yfinance" could not be resolved (reportMissingImports)
/Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/app.py
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/app.py:4:6 - error: Import "dotenv" could not be resolved (reportMissingImports)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/app.py:5:6 - error: Import "fastapi" could not be resolved (reportMissingImports)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/app.py:6:6 - error: Import "fastapi.middleware.cors" could not be resolved (reportMissingImports)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/app.py:7:6 - error: Import "fastapi.staticfiles" could not be resolved (reportMissingImports)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/app.py:8:6 - error: Import "pydantic" could not be resolved (reportMissingImports)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/backend/app.py:104:14 - error: Import "openai" could not be resolved (reportMissingImports)
7 errors, 1 warning, 0 informations

=== PYRIGHT (frontend_py) ===
/Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/frontend_py/app.py
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/frontend_py/app.py:4:8 - warning: Import "requests" could not be resolved from source (reportMissingModuleSource)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/frontend_py/app.py:5:8 - error: Import "streamlit" could not be resolved (reportMissingImports)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/frontend_py/app.py:6:6 - error: Import "dotenv" could not be resolved (reportMissingImports)
  /Volumes/KINGSTON/vic_ai_trainning_class/class_1/exercise_4/frontend_py/app.py:18:32 - error: Type annotation not supported for this statement (reportInvalidTypeForm)
3 errors, 1 warning, 0 informations
