class User {
  final String username;
  final String nombres;
  final String email;

  User({required this.username, required this.nombres, required this.email});

  factory User.fromJson(Map<String, dynamic> json) {
    print("Entro a la clase User $json");
    return User(
      username: json['username'],
      nombres: json['Nombres'],
      email: json['email'] ?? json['correo'] ?? '',
    );
  }
}
