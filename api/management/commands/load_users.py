import random
import random as r

from django.core.management import BaseCommand

from api.models import Contact, User, UserContact


class Command(BaseCommand):
    def generate_phone_number(self):
        ph_no = list()

        # the first number should be in the range of 6 to 9
        ph_no.append(r.randint(6, 9))

        # the for loop is used to append the other 9 numbers.
        # the other 9 numbers can be in the range of 0 to 9.
        for i in range(1, 10):
            ph_no.append(r.randint(0, 9))

        return "".join(str(x) for x in ph_no)

    def get_name(self):
        import random
        import string

        # printing lowercase
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(10))

    def handle(self, *args, **options):
        some_numbers = []
        contacts = []
        for contact_id in range(1, 500):
            phone_number = self.generate_phone_number()
            name = self.get_name()
            contact = Contact.objects.create(number=phone_number, name=name)
            contacts.append(contact)
            if len(some_numbers) < 10:
                some_numbers.append([phone_number, name])
            self.stdout.write(
                self.style.SUCCESS('Successfully created contact "%s"' % contact_id)
            )

        for number in some_numbers:
            user = User.objects.create(phone_number=number[0], name=number[1])
            for i in range(49):
                choice = random.choice(contacts)
                random_contact = contacts.pop(contacts.index(choice))
                UserContact.objects.create(user=user, contact=random_contact)
