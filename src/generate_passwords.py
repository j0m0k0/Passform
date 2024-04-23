import argparse
import ast
import pickle
import torch
import torch.nn.functional as F
import pandas as pd
from modelClass import TransformerModel  # Ensure this import points to your model class correctly
import warnings
warnings.filterwarnings("ignore")

def safe_eval_tuple(input_str):
    try:
        # Safely evaluate the string to a tuple
        result = ast.literal_eval(input_str)
        if isinstance(result, tuple) and all(isinstance(num, int) for num in result):
            return result
        else:
            raise ValueError("The input string does not contain a tuple of integers.")
    except:
        raise ValueError("Invalid input for tuple conversion.")

def load_best_params(file_name):
    # Load the CSV file containing the best parameters
    best_params_df = pd.read_csv(file_name)
    # Convert DataFrame to dictionary
    best_params = best_params_df.to_dict(orient='records')[0]
    return best_params

def load_vocab(file_path):
    with open(file_path, 'rb') as f:
        vocab = pickle.load(f)
    return vocab

def load_model_and_vocab(model_path, vocab_path):
    vocab = load_vocab(vocab_path)
    vocab_size = len(vocab)  # Assume vocab provides a length
    best_params = load_best_params('./params/best_params.csv')

    # Assume parameters are stored directly as usable values in the CSV
    best_num_layers = int(best_params['num_layers'])
    best_dropout_rate = float(best_params['dropout_rate'])
    model_config = safe_eval_tuple(best_params['model_config'])
    best_d_model = int(model_config[0])
    best_nhead = int(model_config[1])

    model = TransformerModel(num_layers=best_num_layers, dropout_rate=best_dropout_rate, vocab_size=vocab_size, d_model=best_d_model, nhead=best_nhead)
    device = torch.device('cpu')  # Change to 'cuda' if GPU is to be used
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)  # Ensure the model is on the correct device

    return model, vocab

def generate_passwords(model, vocab, num_passwords, password_length, device='cpu'):
    model.eval()
    model.to(device)
    stoi = vocab.stoi if hasattr(vocab, 'stoi') else vocab.get_stoi()
    itos = vocab.itos if hasattr(vocab, 'itos') else vocab.get_itos()
    sos_index = stoi['<sos>']
    passwords = []

    for _ in range(num_passwords):
        password = []
        input_seq = torch.tensor([[sos_index]], dtype=torch.long).to(device)

        for _ in range(password_length):
            with torch.no_grad():
                output = model(input_seq)
                probabilities = F.softmax(output[:, -1, :], dim=-1)
                next_token = torch.multinomial(probabilities, 1)
                password.append(itos[next_token.item()])
                next_token = next_token.view(1, 1)
                input_seq = torch.cat([input_seq, next_token], dim=1)

        passwords.append(''.join(password).replace('<eos>', ''))

    return passwords

def main():
    parser = argparse.ArgumentParser(description='Password Generation Script')
    parser.add_argument('-c', '--num_passwords', type=int, required=True, help='Number of passwords to generate')
    parser.add_argument('-l', '--password_length', type=int, required=True, help='Length of each password')
    
    args = parser.parse_args()

    # Example usage
    model, vocab = load_model_and_vocab('models/passform.model', 'vocab/vocab.pkl')
    generated_passwords = generate_passwords(model, vocab, num_passwords=args.num_passwords, password_length=args.password_length)

    for pwd in generated_passwords:
        print(pwd)

if __name__ == "__main__":
    main()
