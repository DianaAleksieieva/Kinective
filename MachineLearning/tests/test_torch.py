import torch

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())

# Create a random tensor
x = torch.rand(5, 3)
print("Random tensor:")
print(x)

# Basic operations
y = torch.rand(5, 3)
z = x + y
print("\nTensor addition result:")
print(z)