rule ransomware_file_extension {
    meta:
        description = "Detects common ransomware file extensions"
    strings:
        $ext1 = ".locked"
        $ext2 = ".encrypted"
        $ext3 = ".crypt"
    condition:
        any of them
}

rule high_entropy_header {
    meta:
        description = "Detects high-entropy file headers typical of encryption"
    strings:
        $high1 = { FF FF FF FF ?? ?? ?? ?? }
    condition:
        $high1 at 0
}
