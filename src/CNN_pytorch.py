import re
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
import numpy as np
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
import torch.nn.functional as F

def preprocess_payload(payload):
    def replace_url(text):
        text = re.sub(r'http[s]?://[^\s"<>]+', 'http://u', text)
        text = re.sub(r'ftp://[^\s"<>]+', 'http://u', text)
        text = re.sub(r'mailto:[^\s"<>]+', 'http://u', text)
        text = re.sub(r'file://[^\s"<>]+', 'http://u', text)
        text = re.sub(r'tel:[^\s"<>]+', 'http://u', text)
        text = re.sub(r'data:[^\s"<>]+', 'http://u', text)
        text = re.sub(r'(href|src|action|formaction|background)=[\'"][^\s"<>]+[\'"]', r'\1="http://u"', text)
        text = re.sub(r'srcset="([^"]+)"', lambda match: 'srcset="r"', text)
    
        return text

    # 替換數字為單個 0
    def replace_numbers(text):
        return re.sub(r'\d+', '0', text)  # 使用 \d+ 確保每組數字只替換為一個 0

    # 保留 HTML 標籤並處理內容
    def process_tag(match):
        tag_content = match.group(0)
        # 替換標籤內的 URL
        tag_content = replace_url(tag_content)
        # 替換標籤內的數字
        tag_content = replace_numbers(tag_content)
        return tag_content

    # 使用正則表達式匹配 HTML 標籤並處理
    processed_payload = re.sub(r'<[^>]+>', process_tag, payload)
        
    # 處理標籤外的數字和 URL
    processed_payload = replace_url(processed_payload)
    processed_payload = replace_numbers(processed_payload)
        
    return processed_payload

def custom_tokenize(text):
    # 定義正則表達式規則
    pattern = r'''(?x)                         # 開啟 verbose 模式，讓正則表達式更易讀
        "[^"]+"                                # 匹配雙引號內的內容
        | '[^']+'                              # 匹配單引號內的內容
        | http://\w+                           # 匹配 http:// 開頭的 URL
        | <\w+>                                # 匹配開啟的 HTML 標籤 <tag>
        | </\w+>                               # 匹配關閉的 HTML 標籤 </tag>
        | \w+=                                 # 匹配像 name=value 這樣的結構
        | [\w\.]+                              # 匹配普通單詞（字母、數字、下劃線或點）
        | [\s]+                                # 匹配空白字符
        | [^\w\s<>]+                           # 匹配非字母數字空白和非標籤的其他字符
    '''
        
    # 使用正則表達式分詞
    tokens = re.findall(pattern, text)
        
    # 清除多餘的空格字符
    tokens = [token.strip() for token in tokens if token.strip()]
        
    return tokens

def tokens_to_vectors(tered_tokensfil, model, max_sequence_length=100):
    vectors = []
    
    for token in tered_tokensfil:
        if token in model.wv:
            vectors.append(torch.tensor(model.wv[token], dtype=torch.float32))  # 轉為 PyTorch Tensor
        else:
            vectors.append(torch.zeros(model.vector_size, dtype=torch.float32))  # 未知詞補零

    vectors = torch.stack(vectors) if vectors else torch.zeros((0, model.vector_size), dtype=torch.float32)  

    # 進行 padding 或截取，確保 shape = (max_sequence_length, embedding_dim)
    if vectors.shape[0] < max_sequence_length:
        pad_size = max_sequence_length - vectors.shape[0]
        padding_tensor = torch.zeros((pad_size, model.vector_size), dtype=torch.float32)
        vectors = torch.cat([vectors, padding_tensor], dim=0)
    else:
        vectors = vectors[:max_sequence_length]  # 超過 max_sequence_length 則截斷

    return vectors

class XSSClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, output_dim, max_seq_len):
        super(XSSClassifier, self).__init__()
        
        # CNN 層
        self.conv1 = nn.Conv1d(in_channels=input_dim, out_channels=6, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(in_channels=input_dim, out_channels=4, kernel_size=3, padding=1)
        self.conv3 = nn.Conv1d(in_channels=input_dim, out_channels=2, kernel_size=3, padding=1)
        
        # BiLSTM 層
        self.lstm = nn.LSTM(input_size=12, hidden_size=64, batch_first=True, bidirectional=True)
        
        # Self-Attention 層
        self.attention = nn.Linear(128, 1)
        
        # MaxPooling & UpSampling
        self.maxpool = nn.MaxPool1d(kernel_size=2)
        self.upsample = nn.Upsample(scale_factor=2, mode='nearest')
        
        # Fully Connected Layers
        self.fc1 = nn.Linear(140 * max_seq_len, 128)
        self.fc2 = nn.Linear(128, output_dim)
        self.dropout = nn.Dropout(0.5)

    def attention_layer(self, lstm_out):
        attn_scores = torch.tanh(self.attention(lstm_out))  # (batch, seq_len, 1)
        attn_weights = torch.softmax(attn_scores, dim=1)  # 計算權重
        attn_out = lstm_out * attn_weights  # 加權輸出
        return attn_out
 
    def forward(self, x):
        # 調整維度 (batch, seq_len, embedding_dim) → (batch, embedding_dim, seq_len)
        x = x.permute(0, 2, 1)
        
        # CNN
        conv1_out = F.relu(self.conv1(x))
        conv2_out = F.relu(self.conv2(x))
        conv3_out = F.relu(self.conv3(x))
        
        # 串接 CNN 特徵
        conv_out = torch.cat([conv1_out, conv2_out, conv3_out], dim=1)  # (batch, 12, seq_len)
        
        # 調整維度以適應 LSTM (batch, seq_len, 12)
        conv_out = conv_out.permute(0, 2, 1)
        
        # BiLSTM
        lstm_out, _ = self.lstm(conv_out)
        
        # Self-Attention
        attn_out = self.attention_layer(lstm_out)
        
        # MaxPooling + UpSampling
        pooled_out = self.maxpool(attn_out.permute(0, 2, 1))  # 變成 (batch, channels, seq_len//2)
        upsampled_out = self.upsample(pooled_out)  # 放大回原本大小 (batch, channels, seq_len)
        
        # 特徵融合
        final_features = torch.cat([conv_out, upsampled_out.permute(0, 2, 1)], dim=-1)  # (batch, seq_len, 128)
        
        # 展平成全連接層輸入
        flattened = final_features.view(final_features.size(0), -1)
        
        # Dropout + 全連接層
        fc1_out = F.relu(self.fc1(flattened))
        fc1_out = self.dropout(fc1_out)
        output = self.fc2(fc1_out)

        return output

class XSSDetector:
    def __init__(self, model_path, word2vec_path, device=None):
        self.device = device or torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.word2vec = Word2Vec.load(word2vec_path)
        self.model = XSSClassifier(128, 64, 2, 100)
        self.model.to(self.device)
        self.model.load_state_dict(torch.load(model_path))
        self.model.eval()

    def is_xss(self, payload):
        with torch.no_grad():
            processed_payload = preprocess_payload(payload)
            tokens = custom_tokenize(processed_payload)
            xss_vector = tokens_to_vectors(tokens, self.word2vec).unsqueeze(0).to(self.device)
            output = self.model(xss_vector)
            _, predicted = torch.max(output, 1)
            return predicted.item()



