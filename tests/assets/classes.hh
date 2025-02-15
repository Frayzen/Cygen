class TestClass {
  class InnerClass {
    void defaultPrivate(int a);
  };
  private:
    int first_privatemethod(int a, int b);
  public:
    TestClass(int* a);
    void test(char o);
  private:
    int second_privatemethod(int a, int b);
};

class SubClass : public TestClass {
  public:
    SubClass(int* b, char c) : TestClass(b){};
    int other();
  private:
};

struct TestStruct {
  struct InnerStruct {
    void defaultPrivate(int a);
  };
  public:
    TestStruct(int* a);
    void test(char o);
  private:
    int privatemethod(int a, int b);
};

struct SubStruct : TestStruct {
  public:
    SubStruct(int* b, char c) : TestStruct(b){};
    int other();
  private:
};
