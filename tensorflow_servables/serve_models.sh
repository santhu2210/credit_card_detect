#!/bin/bash
tensorflow_model_server --port=8500 --rest_api_port=8501 --model_config_file=/tensorflow_servables/serve_models.conf
