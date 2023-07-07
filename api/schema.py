import graphene
from graphene_django.types import DjangoObjectType
from .models import Employee, Department
from graphene_django.filter import DjangoFilterConnectionField
from graphene import  relay
from graphql_relay import from_global_id
from graphql_jwt.decorators import login_required

# Query はMetaを使う
class EmployeeNode(DjangoObjectType):
    class Meta:
        model = Employee
        filter_fields = {
            'name': ['exact', 'icontains'],
            'join_year': ['exact', 'icontains'],
            'department__dept_name': ['icontains']
        }
        # expectが完全一致、icontainsが部分一致
        interfaces = (relay.Node,)


class DepartmentNode(DjangoObjectType):
    class Meta:
        model = Department
        filter_fields = {
            'employees': ['exact'],
            'dept_name': ['exact']
        }
        interfaces = (relay.Node,)

# 部署の作成
class DeptCreateMutation(relay.ClientIDMutation):
    class Input:
        dept_name = graphene.String(required=True)

    department = graphene.Field(DepartmentNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):

        department = Department(
            dept_name=input.get('dept_name')
        )
        department.save()

        return DeptCreateMutation(department=department)

# 削除
class DeptDeleteMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    department = graphene.Field(DepartmentNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):

        department = Department(
            id=from_global_id(input.get('id'))[1]
        )
        department.delete()

        return DeptDeleteMutation(department=None)

# 従業員の作成
class EmployeeCreateMutation(relay.ClientIDMutation):
    class Input:
        name = graphene.String(required=True)
        join_year = graphene.Int(required=True)
        department = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        employee = Employee(
            name=input.get('name'),
            join_year=input.get('join_year'),
            department_id=from_global_id(input.get('department'))[1]
        )
        employee.save()

        return EmployeeCreateMutation(employee=employee)

# 更新
class EmployeeUpdateMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        name = graphene.String(required=True)
        join_year = graphene.Int(required=True)
        department = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):

        employee = Employee.objects.get(id=from_global_id(input.get('id'))[1])
        employee.name = input.get('name')
        employee.join_year = input.get('join_year')
        employee.department_id = from_global_id(input.get('department'))[1]

        employee.save()

        return EmployeeUpdateMutation(employee=employee)

# 削除
class EmployeeDeleteMutation(relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)

    employee = graphene.Field(EmployeeNode)

    @login_required
    def mutate_and_get_payload(root, info, **input):
        employee = Employee(
            id=from_global_id(input.get('id'))[1]
        )
        employee.delete()

        return EmployeeDeleteMutation(employee=None)

# mutationクラスの作成
class Mutation(graphene.AbstractType):
    create_dept = DeptCreateMutation.Field()
    delete_dept = DeptDeleteMutation.Field()
    create_employee = EmployeeCreateMutation.Field()
    update_employee = EmployeeUpdateMutation.Field()
    delete_employee = EmployeeDeleteMutation.Field()


class Query(graphene.ObjectType):
    employee = graphene.Field(EmployeeNode, id=graphene.NonNull(graphene.ID))
    all_employees = DjangoFilterConnectionField(EmployeeNode)
    all_departments = DjangoFilterConnectionField(DepartmentNode)

    @login_required
    def resolve_employee(self, info, **kwargs):
        id = kwargs.get('id')
        if id is not None:
            return Employee.objects.get(id=from_global_id(id)[1])
        # 文字列でわたってくるのでインタジャーに変換する

    @login_required
    def resolve_all_employees(self, info, **kwargs):
        return Employee.objects.all()

    @login_required
    def resolve_all_departments(self, info, **kwargs):
        return Department.objects.all()
