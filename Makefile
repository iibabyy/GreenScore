MAGENTA = \033[35m
BLEU_CLAIR = \033[36m 
RESET = \033[0m

all : frontend backend

frontend :
	docker compose up --build -d

backend :
	(cd backend && python3 -m venv env && . env/bin/activate && pip install -r requirements.txt && echo "API is ready, listening on : http://localhost:8000" && uvicorn app:app)


down : 
	docker compose down

check:
	@echo "$(MAGENTA)CONTAINER:$(RESET)"
	@docker ps -a
	@echo "$(BLEU_CLAIR)------------------------------------------------$(RESET)"
	@echo "$(MAGENTA)IMAGES:$(RESET)"
	@docker images
	@echo "$(BLEU_CLAIR)------------------------------------------------$(RESET)"
	@echo "$(MAGENTA)VOLUMES:$(RESET)"
	@docker volume ls

fclean : down
	docker system prune -af
	docker volume prune -af

log :
	docker compose logs -f

re : fclean all

.PHONY : all up down fclean log re backend frontend