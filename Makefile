.PHONY: test test-v test-specific lint clean

# 默认运行所有测试
test:
	pytest tests/

# 运行测试并显示详细输出
test-v:
	pytest -v tests/

# 运行特定测试（使用引号避免zsh问题）
test-specific:
	@if [ "$(test)" = "" ]; then \
		echo "Usage: make test-specific test='tests/path/to/test.py::TestClass::test_method'"; \
		exit 1; \
	fi; \
	pytest "$(test)" -v

# 运行所有代码检查
lint:
	black .
	flake8 .
	mypy .

# 清理临时文件
clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
	find . -type d -name ".mypy_cache" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete 