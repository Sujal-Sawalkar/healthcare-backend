from rest_framework.test import APITestCase


class HealthcareAPITests(APITestCase):
    def register_and_login(self, email="a@test.com", name="Alice", password="StrongPass#123"):
        r = self.client.post("/api/auth/register/", {"name": name, "email": email, "password": password}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        r = self.client.post("/api/auth/login/", {"email": email, "password": password}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertIn("access", r.data)
        return r.data["access"]

    def auth(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_register_validation(self):
        self.register_and_login()
        r = self.client.post("/api/auth/register/", {"name": "X", "email": "A@test.com", "password": "StrongPass#123"}, format="json")
        self.assertEqual(r.status_code, 400)  # duplicate email (case-insensitive)
        r = self.client.post("/api/auth/register/", {"name": "X", "email": "b@test.com", "password": "123"}, format="json")
        self.assertEqual(r.status_code, 400)  # weak password

    def test_login_wrong_password(self):
        self.register_and_login()
        r = self.client.post("/api/auth/login/", {"email": "a@test.com", "password": "nope"}, format="json")
        self.assertEqual(r.status_code, 401)

    def test_endpoints_require_auth(self):
        for url in ("/api/patients/", "/api/doctors/", "/api/mappings/"):
            self.assertEqual(self.client.get(url).status_code, 401)

    def test_patient_crud_and_isolation(self):
        t1 = self.register_and_login("a@test.com")
        t2 = self.register_and_login("b@test.com", "Bob")
        self.auth(t1)
        r = self.client.post("/api/patients/", {"name": "P1", "age": 30, "gender": "M"}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        pid = r.data["id"]
        self.assertEqual(len(self.client.get("/api/patients/").data), 1)
        self.assertEqual(self.client.put(f"/api/patients/{pid}/", {"name": "P1x", "age": 31, "gender": "M"}, format="json").status_code, 200)
        self.assertEqual(self.client.post("/api/patients/", {"name": "", "age": 999, "gender": "Z"}, format="json").status_code, 400)
        self.auth(t2)
        self.assertEqual(self.client.get("/api/patients/").data, [])
        self.assertEqual(self.client.get(f"/api/patients/{pid}/").status_code, 404)
        self.auth(t1)
        self.assertEqual(self.client.delete(f"/api/patients/{pid}/").status_code, 204)

    def test_doctor_permissions(self):
        t1 = self.register_and_login("a@test.com")
        t2 = self.register_and_login("b@test.com", "Bob")
        self.auth(t1)
        r = self.client.post("/api/doctors/", {"name": "D", "specialization": "Cardio", "email": "d@h.com", "experience_years": 5}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        did = r.data["id"]
        self.auth(t2)
        self.assertEqual(len(self.client.get("/api/doctors/").data), 1)  # everyone sees all doctors
        self.assertEqual(self.client.get(f"/api/doctors/{did}/").status_code, 200)
        self.assertEqual(self.client.delete(f"/api/doctors/{did}/").status_code, 403)  # only creator can delete

    def test_mapping_flow(self):
        t1 = self.register_and_login("a@test.com")
        t2 = self.register_and_login("b@test.com", "Bob")
        self.auth(t1)
        pid = self.client.post("/api/patients/", {"name": "P", "age": 20, "gender": "F"}, format="json").data["id"]
        did = self.client.post("/api/doctors/", {"name": "D", "specialization": "Neuro", "email": "d@h.com"}, format="json").data["id"]
        r = self.client.post("/api/mappings/", {"patient": pid, "doctor": did}, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        mid = r.data["id"]
        self.assertEqual(self.client.post("/api/mappings/", {"patient": pid, "doctor": did}, format="json").status_code, 400)  # duplicate
        self.assertEqual(len(self.client.get("/api/mappings/").data), 1)
        r = self.client.get(f"/api/mappings/{pid}/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data[0]["doctor_detail"]["name"], "D")
        # another user can't map to / see / delete someone else's patient
        self.auth(t2)
        self.assertEqual(self.client.post("/api/mappings/", {"patient": pid, "doctor": did}, format="json").status_code, 400)
        self.assertEqual(self.client.get(f"/api/mappings/{pid}/").status_code, 404)
        self.assertEqual(self.client.delete(f"/api/mappings/{mid}/").status_code, 404)
        self.auth(t1)
        self.assertEqual(self.client.delete(f"/api/mappings/{mid}/").status_code, 204)
        self.assertEqual(self.client.get(f"/api/mappings/{pid}/").data, [])
