class User {
  final String username;
  final String nombres;

  User({required this.username, required this.nombres});

  factory User.fromJson(Map<String, dynamic> json) {
    print("Entro a la clase User $json");
    return User(
      username: json['username'],
      nombres: json['Nombres'],
    );
  }
}
