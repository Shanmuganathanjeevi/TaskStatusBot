from model2vec import StaticModel

print("Pre-downloading Model2Vec...")
model = StaticModel.from_pretrained("minishlab/potion-base-8M")
print("✓ Model ready")