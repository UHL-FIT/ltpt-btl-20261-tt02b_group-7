[Setup]
; Thông tin chung về ứng dụng
AppName=SmartAttend
AppVersion=1.0
AppPublisher=Khoa CNTT
AppPublisherURL=https://example.com/
AppSupportURL=https://example.com/
AppUpdatesURL=https://example.com/
DefaultDirName={autopf}\SmartAttend
DisableProgramGroupPage=yes
; Tên file cài đặt đầu ra
OutputBaseFilename=Setup_SmartAttend
; Thêm icon cho file Setup
SetupIconFile=assets\app_icon.ico
; Thư mục lưu file cài đặt (để vào thư mục dist)
OutputDir=dist
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; Thư mục bản GUI
Source: "dist\SmartAttend\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
; Thư mục bản CLI (ghi đè các thư viện trùng lặp vào cùng bộ cài)
Source: "dist\SmartAttend_CLI\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
; Tạo shortcut ở Start Menu cho cả GUI và CLI
Name: "{autoprograms}\SmartAttend"; Filename: "{app}\SmartAttend.exe"
Name: "{autoprograms}\SmartAttend (CLI)"; Filename: "{app}\SmartAttend_CLI.exe"
; Tạo shortcut ở Desktop cho bản GUI nếu user tick chọn
Name: "{autodesktop}\SmartAttend"; Filename: "{app}\SmartAttend.exe"; Tasks: desktopicon

[Run]
; Chạy ứng dụng sau khi cài đặt xong
Filename: "{app}\SmartAttend.exe"; Description: "{cm:LaunchProgram,SmartAttend}"; Flags: nowait postinstall skipifsilent
