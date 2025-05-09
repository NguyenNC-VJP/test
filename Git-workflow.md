# 🚀 Git Workflow Chuẩn Cho Dự Án

Quy trình làm việc với Git theo chuẩn `feature -> develop -> main` giúp team làm việc hiệu quả và kiểm soát release rõ ràng.

---
0. Tạo issues để giải quyết dựa theo schedule 
1. Tạo Nhánh Mới Từ `develop`
git checkout develop
git pull origin develop
git checkout -b feature/<ten-tinh-nang>-<ten-nguoi-tao>
    vd: git checkout -b feature/login-nguyen

2. Làm Việc Trên Nhánh `feature`
# Sau khi code xong
git add .
git commit -m "<mã-id-issues>-feat: mô tả tính năng rõ ràng"
    vd: git commit -m "#1-feat: Đã tạo xong phần login"
git push origin feature/login-nguyen

3. Hợp nhất `feature` vào `develop`
git checkout develop
git pull origin develop
git merge feature/login-nguyen
git push origin develop

4. Đưa `feature` lên `main` để release
git checkout main
git pull origin main
git merge develop
git push origin main

5. Gắn tag cho bản phát hành:
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
===================================================
🔖 Ghi Chú
feature/: dùng cho các tính năng mới.

develop: nhánh tích hợp và kiểm thử.

main: nhánh production, chứa phiên bản chính thức.

hotfix/: dùng khi cần sửa lỗi gấp trên production (có thể thêm sau).

✅ Lưu ý
Hạn chế đẩy nhánh feature lên thẳng main mà không thông qua kiểm thử kỹ càng
Luôn pull nhánh trước khi bắt đầu.
Tạo pull request để review code nếu làm việc nhóm.
Viết commit message rõ ràng theo định dạng: #?-feat:, fix:, v.v.
===================================================
★  Other:
1. Xoá nhánh ở local
git branch -d feature/login-nguyen
2. Xoá nhánh trên remote
git push origin --delete feature/login-nguyen
3. Kiểm tra lại nhánh còn tồn tại hay không
Danh sách local: git branch
Danh sách remote: git branch -r