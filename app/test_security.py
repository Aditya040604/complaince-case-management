from app.auth.security import hash_password, verify_password

password = "Aditya@1234"

hashed_password = hash_password(password)

print("Password:", password)
print("Hashed_password:", hashed_password)

print("Correct password", verify_password(password, hashed_password))

print("Wrong password", verify_password("Vikram", hashed_password))