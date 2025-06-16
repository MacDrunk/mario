from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Tarea

class TareaModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser_model', # Changed to avoid collision
            password='testpassword'
        )

    def test_tarea_creation(self):
        tarea = Tarea.objects.create(
            usuario=self.user,
            titulo='Test Tarea Model', # Changed to be specific
            descripccion='This is a test tarea model.'
        )
        self.assertEqual(tarea.titulo, 'Test Tarea Model')
        self.assertEqual(tarea.descripccion, 'This is a test tarea model.')
        self.assertFalse(tarea.completo)
        self.assertEqual(tarea.usuario, self.user)

    def test_tarea_str_representation(self):
        tarea = Tarea.objects.create(
            usuario=self.user,
            titulo='My Test Tarea Str', # Changed to be specific
            descripccion='Another test tarea str.'
        )
        self.assertEqual(str(tarea), 'My Test Tarea Str')

    def test_tarea_ordering(self):
        tarea1 = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Model Incompleta', # Changed to be specific
            descripccion='This tarea is incomplete for model test.',
            completo=False
        )
        tarea2 = Tarea.objects.create(
            usuario=self.user,
            titulo='Tarea Model Completa', # Changed to be specific
            descripccion='This tarea is complete for model test.',
            completo=True
        )

        tareas = Tarea.objects.filter(usuario=self.user).order_by('completo') # Explicit order for clarity
        self.assertEqual(tareas[0], tarea1)
        self.assertEqual(tareas[1], tarea2)

class AuthViewsTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user( # This is self.user for AuthViewsTest
            username='testauthuser',
            password='testauthpassword',
            email='testauthuser@example.com'
        )
        self.client = Client()

    # Registration Tests (PaginaRegistro)
    def test_registration_page_get(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)

    def test_user_registration_successful(self):
        user_count_before = User.objects.count()
        response = self.client.post(reverse('registro'), {
            'username': 'testuser_reg',
            'password1': 'password123',
            'password2': 'password123',
        })
        self.assertRedirects(response, reverse('tarea'))
        self.assertEqual(User.objects.count(), user_count_before + 1)
        self.assertIn('_auth_user_id', self.client.session)
        # new_user = User.objects.get(username='testuser_reg') # Getting by username
        # self.assertEqual(self.client.session['_auth_user_id'], str(new_user.id)) # Comparing string id
        # Ensure the logged-in user is the one just created
        self.assertTrue(User.objects.filter(username='testuser_reg').exists())
        logged_in_user_id = self.client.session['_auth_user_id']
        created_user_id = str(User.objects.get(username='testuser_reg').pk)
        self.assertEqual(logged_in_user_id, created_user_id)


    def test_authenticated_user_redirected_from_registration(self):
        self.client.login(username='testauthuser', password='testauthpassword')
        response = self.client.get(reverse('registro'))
        self.assertRedirects(response, reverse('tarea'))

    # Login Tests (Logueo)
    def test_login_page_get(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_user_login_successful(self):
        response = self.client.post(reverse('login'), {
            'username': 'testauthuser',
            'password': 'testauthpassword',
        })
        self.assertRedirects(response, reverse('tarea'))
        self.assertIn('_auth_user_id', self.client.session)
        self.assertEqual(self.client.session['_auth_user_id'], str(self.user.id))


    def test_user_login_invalid_credentials(self):
        response = self.client.post(reverse('login'), {
            'username': 'testauthuser',
            'password': 'wrongpassword',
        })
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected_from_login(self):
        self.client.login(username='testauthuser', password='testauthpassword')
        response = self.client.get(reverse('login'))
        self.assertRedirects(response, reverse('tarea'))

    # Logout Test (Logout)
    def test_user_logout(self):
        self.client.login(username='testauthuser', password='testauthpassword')
        self.assertIn('_auth_user_id', self.client.session)

        response = self.client.get(reverse('logout'))
        self.assertNotIn('_auth_user_id', self.client.session)
        self.assertRedirects(response, reverse('login'))

class TareaViewsTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(username='user1_crud', password='password1')
        self.user2 = User.objects.create_user(username='user2_crud', password='password2')
        self.tarea1 = Tarea.objects.create(usuario=self.user1, titulo='Tarea 1 User 1', descripccion='Description for Tarea 1')
        self.client = Client()

    # ListaPendientes Tests
    def test_list_pendientes_authenticated(self):
        self.client.login(username='user1_crud', password='password1')
        response = self.client.get(reverse('tarea'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tarea1.titulo)

    def test_list_pendientes_search(self):
        self.client.login(username='user1_crud', password='password1')
        Tarea.objects.create(usuario=self.user1, titulo='UniqueTitleSearch', descripccion='Searchable task')
        response = self.client.get(reverse('tarea') + '?buscar-texto=UniqueTitleSearch')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'UniqueTitleSearch')
        self.assertNotContains(response, self.tarea1.titulo)

        # Test searching for the original task
        response_orig = self.client.get(reverse('tarea') + '?buscar-texto=Tarea 1 User 1')
        self.assertEqual(response_orig.status_code, 200)
        self.assertContains(response_orig, self.tarea1.titulo)
        self.assertNotContains(response_orig, 'UniqueTitleSearch')


    def test_list_pendientes_unauthenticated(self):
        response = self.client.get(reverse('tarea'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('tarea')}")

    # DetalleTarea Tests
    def test_detalle_tarea_authenticated_owner(self):
        self.client.login(username='user1_crud', password='password1')
        response = self.client.get(reverse('tarea', args=[self.tarea1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tarea1.titulo)

    def test_detalle_tarea_authenticated_not_owner(self):
        self.client.login(username='user2_crud', password='password2')
        response = self.client.get(reverse('tarea', args=[self.tarea1.pk]))
        self.assertEqual(response.status_code, 404) # DetailView returns 404 if object not found in queryset

    def test_detalle_tarea_unauthenticated(self):
        response = self.client.get(reverse('tarea', args=[self.tarea1.pk]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('tarea', args=[self.tarea1.pk])}")

    # CrearTarea Tests
    def test_crear_tarea_get_authenticated(self):
        self.client.login(username='user1_crud', password='password1')
        response = self.client.get(reverse('crear-tarea'))
        self.assertEqual(response.status_code, 200)

    def test_crear_tarea_post_authenticated(self):
        self.client.login(username='user1_crud', password='password1')
        task_count_before = Tarea.objects.filter(usuario=self.user1).count()
        response = self.client.post(reverse('crear-tarea'), {
            'titulo': 'New Task Title Create',
            'descripccion': 'Description for new task',
            'completo': False
        })
        self.assertRedirects(response, reverse('tarea'))
        self.assertTrue(Tarea.objects.filter(usuario=self.user1, titulo='New Task Title Create').exists())
        self.assertEqual(Tarea.objects.filter(usuario=self.user1).count(), task_count_before + 1)


    def test_crear_tarea_unauthenticated_get(self): # Renamed for clarity
        response = self.client.get(reverse('crear-tarea'))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('crear-tarea')}")

    def test_crear_tarea_unauthenticated_post(self): # Renamed for clarity
        response = self.client.post(reverse('crear-tarea'), {
            'titulo': 'Attempted Task Title',
            'descripccion': 'Description',
            'completo': False
        })
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('crear-tarea')}")


    # EditarTarea Tests
    def test_editar_tarea_get_authenticated_owner(self):
        self.client.login(username='user1_crud', password='password1')
        response = self.client.get(reverse('editar-tarea', args=[self.tarea1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tarea1.titulo)

    def test_editar_tarea_post_authenticated_owner(self):
        self.client.login(username='user1_crud', password='password1')
        updated_title = 'Updated Tarea 1 Title'
        response = self.client.post(reverse('editar-tarea', args=[self.tarea1.pk]), {
            'titulo': updated_title,
            'descripccion': self.tarea1.descripccion, # Use original descripccion
            'completo': self.tarea1.completo
        })
        self.assertRedirects(response, reverse('tarea'))
        self.tarea1.refresh_from_db()
        self.assertEqual(self.tarea1.titulo, updated_title)

    def test_editar_tarea_get_authenticated_not_owner(self):
        self.client.login(username='user2_crud', password='password2')
        response = self.client.get(reverse('editar-tarea', args=[self.tarea1.pk]))
        self.assertEqual(response.status_code, 404) # UpdateView's get_object filters by user

    def test_editar_tarea_post_authenticated_not_owner(self):
        self.client.login(username='user2_crud', password='password2')
        original_title = self.tarea1.titulo
        response = self.client.post(reverse('editar-tarea', args=[self.tarea1.pk]), {
            'titulo': 'Attempted Update by User2',
            'descripccion': self.tarea1.descripccion,
            'completo': self.tarea1.completo
        })
        self.assertEqual(response.status_code, 404) # UpdateView's get_object filters by user for POST too
        self.tarea1.refresh_from_db()
        self.assertEqual(self.tarea1.titulo, original_title) # Title should not have changed

    def test_editar_tarea_unauthenticated_get(self): # Renamed for clarity
        response = self.client.get(reverse('editar-tarea', args=[self.tarea1.pk]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('editar-tarea', args=[self.tarea1.pk])}")

    def test_editar_tarea_unauthenticated_post(self): # Renamed for clarity
        response = self.client.post(reverse('editar-tarea', args=[self.tarea1.pk]), {'titulo': 'Unauthorized Update'})
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('editar-tarea', args=[self.tarea1.pk])}")

    # Eliminartarea Tests
    def test_eliminar_tarea_get_authenticated_owner(self):
        self.client.login(username='user1_crud', password='password1')
        response = self.client.get(reverse('eliminar-tarea', args=[self.tarea1.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.tarea1.titulo) # Confirmation page should show title

    def test_eliminar_tarea_post_authenticated_owner(self):
        self.client.login(username='user1_crud', password='password1')
        tarea_pk = self.tarea1.pk
        response = self.client.post(reverse('eliminar-tarea', args=[tarea_pk]))
        self.assertRedirects(response, reverse('tarea'))
        self.assertFalse(Tarea.objects.filter(pk=tarea_pk).exists())

    def test_eliminar_tarea_get_authenticated_not_owner(self):
        self.client.login(username='user2_crud', password='password2')
        response = self.client.get(reverse('eliminar-tarea', args=[self.tarea1.pk]))
        self.assertEqual(response.status_code, 404)

    def test_eliminar_tarea_post_authenticated_not_owner(self):
        self.client.login(username='user2_crud', password='password2')
        tarea_pk = self.tarea1.pk
        response = self.client.post(reverse('eliminar-tarea', args=[tarea_pk]))
        self.assertEqual(response.status_code, 404) # DeleteView's get_object filters by user for POST
        self.assertTrue(Tarea.objects.filter(pk=tarea_pk).exists()) # Task should still exist

    def test_eliminar_tarea_unauthenticated_get(self): # Renamed for clarity
        response = self.client.get(reverse('eliminar-tarea', args=[self.tarea1.pk]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('eliminar-tarea', args=[self.tarea1.pk])}")

    def test_eliminar_tarea_unauthenticated_post(self): # Renamed for clarity
        response = self.client.post(reverse('eliminar-tarea', args=[self.tarea1.pk]))
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('eliminar-tarea', args=[self.tarea1.pk])}")
