"""
            đây đươc gọi là chiến lưc in giấy lộn theo kiểu người viêt. nhà cái đưa cổ phiếu lên cao
            mục tiêu: thu hút ánh nhìn của mọi người và niem tin của ndt đang năm giữ co phieu

            cách choi:

            1. scan 1 só trang web để lấy thông tin sắp toi pha loãng cp
            2. chờ giá về vùng quá bán + support mới vào lệnh
            3. chốt lời hoặc lỗ vùng kháng cự và truoc ngày hưởng quyền

            """
from vnstock import *
from vnstock import register_user

register_user(api_key='vnstock_366108191e0a3190950b24d2a04fe157')
# Khởi tạo đối tượng với mã cổ phiếu cần tra cứu (ví dụ: VNM, HPG)


ref = Reference()

# Tra cứu thông tin công ty VCB (Vietcombank)
# print( ref.company("hcm").info())

# df_events = ref.company("hcm").events()


print (ref.columns)


