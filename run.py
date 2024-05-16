from run_functions import run_normal_game, run_ai_agent, load_model_and_play


if __name__ == '__main__':
    # run_normal_game()
    run_ai_agent(graphics=False, graph=True, fps=1024, gamma=0.95)
    # load_model_and_play("model.pth", game_fps=10)
