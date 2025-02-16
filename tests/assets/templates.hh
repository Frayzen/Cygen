template <typename Type> class TestClass {
  class InnerClass {
    void defaultPrivate(int a);
  };

private:
  Type first_privatemethod(Type a, Type b);

public:
  TestClass(Type *a);
  void test(char o);

  template <typename OtherType> OtherType test(OtherType a);
  template <int val> void test(int a);

private:
  int second_privatemethod(int a, int b);
};
