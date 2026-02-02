import torch

def manual_bce_with_logits_loss(logits, targets, pos_weight=5.0):
    max_val = torch.relu(logits)
    stable_log_exp = max_val + torch.log(torch.exp(-max_val) + torch.exp(logits - max_val))

    # 정답(target=1)인 경우의 로스: pos_weight 적용
    # pos_loss = targets * (stable_log_exp - logits) * pos_weight
    pos_loss = targets * (stable_log_exp - logits) * pos_weight

    # 오답(target=0)인 경우의 로스: 가중치 1배
    # neg_loss = (1 - targets) * stable_log_exp
    neg_loss = (1 - targets) * stable_log_exp

    return (pos_loss + neg_loss).mean()