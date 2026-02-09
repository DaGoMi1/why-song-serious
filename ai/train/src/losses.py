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

def focal_binary_cross_entropy_with_logits(logits, targets, alpha=0.8, gamma=2.0):
    # p_t가 1에 가까울수록 모델이 문제를 잘 맞춘 것
    # p_t가 0에 가까울수록 모델이 문제를 못 맞춘 것
    p = torch.sigmoid(logits)
    p_t = targets * p + (1 - targets) * (1 - p)
    
    # pos:neg 데이터 비율이 1:4이므로, 희소한 데이터에 4배의 중요도를 줌
    alpha_t = targets * alpha + (1 - targets) * (1 - alpha)
    
    # 기본 BCE Loss
    ce_loss = torch.nn.functional.binary_cross_entropy_with_logits(logits, targets, reduction='none')
    
    # p_t가 1에 가까울수록 (=모델이 쉽게 정답을 맞힐수록)
    # 전체 Loss 가중치가 낮아짐
    # p_t가 0에 가까울수록 (=모델이 맞추기 어려워할수록)
    # 전체 Loss 가중치가 커짐
    loss = alpha_t * (1 - p_t) ** gamma * ce_loss
    
    return loss.mean()