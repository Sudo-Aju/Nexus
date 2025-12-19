from nex.sys.vault import vault

def test_vault():
    print("Unlocking vault...")
    vault.unlock("super_secret_password")
    
    original = "secret_api_key_123"
    print(f"Original: {original}")
    
    encrypted = vault.encrypt(original)
    print(f"Encrypted: {encrypted}")
    
    decrypted = vault.decrypt(encrypted)
    print(f"Decrypted: {decrypted}")
    
    assert original == decrypted
    assert original != encrypted
    print("Vault verification passed!")

if __name__ == "__main__":
    test_vault()
