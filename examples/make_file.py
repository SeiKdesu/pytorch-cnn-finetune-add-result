from datetime import datetime
import os
import warnings
warnings.filterwarnings("ignore")

def get_time_based_directory(result_dir='result'):
    # 実行時間を使って新しいディレクトリを生成
    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # 年月日_時分秒形式
    time_dir = os.path.join(result_dir, current_time)
    
    # ディレクトリが存在しなければ作成
    if not os.path.exists(time_dir):
        os.makedirs(time_dir)
    
    return time_dir

# ディレクトリは1度だけ生成して保持
